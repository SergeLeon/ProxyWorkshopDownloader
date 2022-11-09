import requests

import re
from urllib.parse import urlparse

import steam
from config import mods_path


def get_search_page(query):
    search_page_url = fr"https://store.steampowered.com/search/{query}"
    resp = requests.get(search_page_url)
    content = replace_search_links(resp.text)
    return content


def replace_search_links(html: str):
    regex = re.compile(r"https://store.steampowered.com/app/\d*/.*/\?snr=\d*_\d*_\d*_\d*_\d*_\d*")
    links = regex.findall(html)

    for link in links:
        html = html.replace(link, f"/browse/?appid={extract_app_id(link)}")

    return html


def extract_app_id(link: str):
    parsed = urlparse(link)
    return parsed.path.split("/")[2]


def get_workshop_list_page(app_id, query="&browsesort=trend&section=readytouseitems"):
    workshop_url = fr"https://steamcommunity.com/workshop/browse/?appid={app_id}{query}"
    resp = requests.get(workshop_url)
    content = replace_workshop_links(resp.text, app_id)

    if "collections" in query:
        content = replace_collection_links(content)

    return content


def replace_collection_links(html):
    regex = re.compile(r"https://steamcommunity.com/sharedfiles/filedetails/\?id=\d*")
    links = regex.findall(html)

    for link in links:
        collection_id = link.split("id=")[-1]
        html = html.replace(link, f"/collection/{collection_id}")

    return html


def replace_workshop_links(html: str, app_id: int):
    regex = re.compile(r"https://steamcommunity.com/sharedfiles/filedetails/\?id=\d*&searchtext=")
    links = regex.findall(html)

    for link in links:
        workshop_id = extract_workshop_id(link)
        html = html.replace(link, f"/{app_id}/{workshop_id}")
        html = add_workshop_button(html,
                                   f'<div id="sharedfile_{workshop_id}" class="workshopItemPreviewHolder  aspectratio_16x9">',
                                   app_id, workshop_id)
    html = html.replace("https://steamcommunity.com/workshop/browse/", "")
    return html


def extract_workshop_id(link: str):
    parsed = urlparse(link)
    return parsed.query[3:-12]


def add_workshop_button(html, element, app_id, workshop_id):
    button = f"""<div class="workshopItemSubscriptionControls aspectratio_16x9">
							<span class="action_wait" id="action_wait_{workshop_id}" style="display: none;"><img src="https://community.akamai.steamstatic.com/public/images/login/throbber.gif"></span>
							<span onclick="fetch('/{app_id}/{workshop_id}/download'); return false;" id="SubscribeItemBtn{workshop_id}" class="general_btn subscribe ">
								<div class="subscribeIcon"></div>
							</span>
						</div>"""
    html = html.replace(element, element + button)

    return html


def get_workshop_page(app_id, workshop_id):
    workshop_url = fr"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}&searchtext="
    resp = requests.get(workshop_url)
    content = replace_workshop_button_action(resp.text)
    return content


def replace_workshop_button_action(html: str):
    html = html.replace('"SubscribeItem();"', r"fetch('download')")
    return html


def replace_collection_buttons(html):
    regex = re.compile('<a onclick="SubscribeCollectionItem(.*);"')
    links = regex.findall(html)

    for link in links:
        app_id, workshop_id = link.strip(" ()").replace("'", "").split(", ")
        html = html.replace(f'onclick="SubscribeCollectionItem{link};"',
                            f"onclick=\"fetch('/{app_id}/{workshop_id}/download'); return false;\"")

    return html


def get_collection_page(collection_id):
    workshop_url = fr"https://steamcommunity.com/sharedfiles/filedetails/?id={collection_id}"
    resp = requests.get(workshop_url)
    content = resp.text
    content = replace_collection_buttons(content)
    return content


def download(app_id, workshop_id):
    steam.workshop_download(app_id, workshop_id, mods_path)
