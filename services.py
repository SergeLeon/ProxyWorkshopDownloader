import re
from os import getcwd
from pathlib import Path

import requests

import steam

mods_path = Path(getcwd()) / "mods"


def add_folder_selector(html):
    regex = re.compile("""<a class="header_installsteam_btn_content".*\n.*</a>""")

    for obj in regex.findall(html):
        html = html.replace(obj,
                            f"""<form action="/folder" method="post" class="header_installsteam_btn_content">
                                <input type="search" 
                                 value="{mods_path}" 
                                 onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';"
                                 name="mods_folder" id="mods_folder">
                                 <button>Submit</button>
                                </form>""")
    return html


def get_search_page(query, headers=""):
    search_page_url = fr"https://store.steampowered.com/search/{query}"
    resp = requests.get(search_page_url, headers=headers)
    html = resp.text
    html = add_folder_selector(html)
    html = fix_search_button(html)
    html = replace_search_links(html)
    return html


def fix_search_button(html):
    regex = re.compile(
        """(<button type="submit" class="btnv6_blue_hoverfade btn_small" data-gpnav="item">.*\n(.*)\n.*</button>)""")

    for obj in regex.findall(html):
        button, span = obj
        html = html.replace(button,
                            f"""<button type="submit" class="btnv6_blue_hoverfade btn_small" data-gpnav="item" 
                            onClick="window.location.reload();">
                            {span}
                            </button>""")
    return html


def replace_search_links(html: str):
    regex = re.compile(r"https://store.steampowered.com/app/(\d*)/(.*)/\?snr=(\d*_\d*_\d*_\d*_\d*_\d*)")
    links = regex.findall(html)

    for link in links:
        app_id, app_name, snr = link
        html = html.replace(f"https://store.steampowered.com/app/{app_id}/{app_name}/?snr={snr}",
                            f"/browse/?appid={app_id}")

    return html


def get_workshop_list_page(app_id, query="&browsesort=trend&section=readytouseitems", headers=""):
    workshop_url = fr"https://steamcommunity.com/workshop/browse/?appid={app_id}{query}"
    resp = requests.get(workshop_url, headers=headers)
    html = resp.text
    html = add_folder_selector(html)
    html = replace_workshop_links(html, app_id)

    if "collections" in query:
        html = replace_collection_links(html, app_id)

    return html


def replace_collection_links(html, app_id):
    regex = re.compile(r"https://steamcommunity.com/sharedfiles/filedetails/\?id=(\d*)")
    links = regex.findall(html)

    for link in links:
        collection_id = link
        html = html.replace(f"https://steamcommunity.com/sharedfiles/filedetails/?id={collection_id}",
                            f"/{app_id}/{collection_id}")

    return html


def replace_workshop_links(html: str, app_id: int):
    regex = re.compile(r"https://steamcommunity.com/sharedfiles/filedetails/\?id=(\d*)&searchtext=")
    links = regex.findall(html)

    for link in links:
        workshop_id = link
        html = html.replace(f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}&searchtext=",
                            f"/{app_id}/{workshop_id}/?searchtext=")

        html = add_workshop_button(html,
                                   (f'<div id="sharedfile_{workshop_id}" class="workshopItemPreviewHolder ">',
                                    f'<div id="sharedfile_{workshop_id}" class="workshopItemPreviewHolder  aspectratio_16x9">'),
                                   app_id, workshop_id)

    html = html.replace("https://steamcommunity.com/workshop/browse/", "")
    return html


def add_workshop_button(html, elements, app_id, workshop_id):
    button = f"""<div class="workshopItemSubscriptionControls aspectratio_16x9">
							<span class="action_wait" id="action_wait_{workshop_id}" style="display: none;"><img src="https://community.akamai.steamstatic.com/public/images/login/throbber.gif"></span>
							<span onclick="fetch('/{app_id}/{workshop_id}/download'); return false;" id="SubscribeItemBtn{workshop_id}" class="general_btn subscribe ">
								<div class="subscribeIcon"></div>
							</span>
						</div>"""

    for element in sorted(elements, key=len):
        if element in html:
            element = element
            break

    html = html.replace(element, element + button)

    return html


def get_workshop_page(app_id, workshop_id, query, headers=""):
    workshop_url = fr"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}&{query}"
    resp = requests.get(workshop_url, headers=headers)
    html = resp.text
    html = add_folder_selector(html)
    html = replace_workshop_button_action(html)
    html = replace_workshop_page_links(html, app_id)
    html = replace_collections_links(html, app_id)
    html = replace_collection_buttons(html)
    return html


def replace_workshop_button_action(html: str):
    html = html.replace('"SubscribeItem();"', r"fetch('download')")
    return html


def replace_workshop_page_links(html: str, app_id):
    regex = re.compile(r'https://steamcommunity.com/sharedfiles/filedetails/\?id=(\d*)')
    links = regex.findall(html)

    for link in links:
        workshop_id = link
        html = html.replace(f'https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}',
                            f"/{app_id}/{workshop_id}/")

    return html


def replace_collections_links(html: str, app_id):
    regex = re.compile(r'https://steamcommunity.com/.*/filedetails/\?id=(\d*)')
    links = regex.findall(html)

    for link in links:
        collection_id = link
        html = html.replace(f'https://steamcommunity.com/workshop/filedetails/?id={collection_id}',
                            f"/{app_id}/{collection_id}/")
        html = html.replace(f'https://steamcommunity.com/sharedfiles/filedetails/?id={collection_id}',
                            f"/{app_id}/{collection_id}/")

    return html


def replace_collection_buttons(html):
    regex = re.compile('<a onclick="SubscribeCollectionItem(.*);"')
    links = regex.findall(html)

    for link in links:
        app_id, workshop_id = link.strip(" ()").replace("'", "").split(", ")
        html = html.replace(f'onclick="SubscribeCollectionItem{link};"',
                            f"onclick=\"fetch('/{app_id}/{workshop_id}/download'); return false;\"")

    return html


def download(app_id, workshop_id):
    mods_path.mkdir(parents=True, exist_ok=True)
    steam.workshop_download(app_id, workshop_id, mods_path)


def init_new_mods_path(path):
    if path:
        global mods_path
        mods_path = Path(path)
