from flask import Flask, request, redirect

from services import get_search_page, get_workshop_page, get_workshop_list_page, get_collection_page, download

app = Flask(__name__)


@app.route("/")
def index():
    return redirect("/search/")


@app.route("/search/")
def search():
    query = request.url.split("/search/")[-1]
    return get_search_page(query=query)


@app.route("/browse/")
def workshop_list():
    app_id = request.args["appid"]
    query = request.url.split(app_id)[-1]
    return get_workshop_list_page(app_id, query)


@app.route("/<int:app_id>/<int:workshop_id>/")
def workshop_page(app_id, workshop_id):
    return get_workshop_page(app_id, workshop_id)


@app.route("/collection/<int:collection_id>")
def collection(collection_id):
    return get_collection_page(collection_id)


@app.route("/<int:app_id>/<int:workshop_id>/download")
def download_workshop(app_id, workshop_id):
    download(app_id, workshop_id)
    return "downloaded"


if __name__ == "__main__":
    import webbrowser

    webbrowser.open('http://127.0.0.1:5000')

    app.run()
