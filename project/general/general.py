from flask import Blueprint
from flask import render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort  # allows for 404 not found responses

ROWS_PER_PAGE = 5

general = Blueprint(
    "general",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/assets",
)


@general.route("/")  # A GET request by default
def home():
    return render_template("public_landing_page.html")
