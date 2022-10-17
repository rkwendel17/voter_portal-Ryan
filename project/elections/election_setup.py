from flask import redirect, render_template, request, Blueprint, flash, url_for
from project.general.models import Users
from admins.models import Precincts

ec_setup = Blueprint(
    "ec_setup",
    __name__,
    template_folder="templates",
    static_folder="static",
)
