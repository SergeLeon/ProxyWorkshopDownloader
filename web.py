from flask import Flask, request, redirect

from services import get_search_page, get_workshop_page, get_workshop_list_page, download, init_new_mods_path

app = Flask(__name__)


def get_headers():
    headers = dict(request.headers)
    headers.pop("Host")
    return headers


@app.route("/")
def index():
    return redirect("/search/")


@app.route("/folder", methods=["POST"])
def select_folder():
    mods_folder = request.form["mods_folder"]
    init_new_mods_path(mods_folder)
    return redirect(request.referrer)


@app.route("/search/")
def search():
    query = request.url.split("/search/")[-1]
    return get_search_page(query=query, headers=get_headers())


@app.route("/browse/")
def workshop_list():
    app_id = request.args["appid"]
    query = request.url.split("/")[-1]
    return get_workshop_list_page(app_id, query, headers=get_headers())


@app.route("/<int:app_id>/<int:workshop_id>/")
def workshop_page(app_id, workshop_id):
    query = request.url.split("?", 1)[-1]
    return get_workshop_page(app_id, workshop_id, query=query, headers=get_headers())


@app.route("/<int:app_id>/<int:workshop_id>/download")
def download_workshop(app_id, workshop_id):
    download(app_id, workshop_id)
    return "downloaded"


if __name__ == "__main__":
    import webbrowser

    webbrowser.open('http://127.0.0.1:5000')

    app.run()
