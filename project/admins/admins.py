import re

from flask import Blueprint
from flask_login import login_required

from project.general.models import Users
from project.models import db
from flask import render_template, request, url_for, flash, redirect
from project.admins.models import ElectionsMock, RacesMock, CanidateMock, Ballot

from project.user_profiles.models import Address
from project.user_profiles.user_profiles import (
    get_pending_users,
    get_user,
    get_managers,
    verify_address,
)
from project.admins.models import Precincts, ZipRanges

# TODO: Convert all URLs to url_for's
# TODO: resolve DB injection security issues

admins = Blueprint(
    "admins",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/admins",
)


@admins.route("/pending_registrations")
def pending_registrations():
    page = request.args.get("page", 1, type=int)
    users = get_pending_users(page=page)
    return render_template("admins/pending_registration_index.html", users=users)


@admins.route("/verify_registration/<int:id>")
def verify_registration(id):
    user = get_user(id)
    return render_template("admins/verify_registration.html", user=user)


@admins.route("/precinct/new", methods=("GET", "POST"))
@login_required
def create_precinct():
    managers = get_managers()
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        precinct_name = request.form["precinct_name"]
        poll_manager_id = request.form["poll_manager"]
        ship_address = request.form["ship-address"]
        address2 = request.form["address2"]
        locality = request.form["locality"]
        state = request.form["state"]
        postcode = request.form["postcode"]
        country = request.form["country"]

        if not re.match(r"^\d{3}-\d{3}-\d{4}$", phone_number):
            flash("Invalid phone number format, please follow the form xxx-xxx-xxxx.")
            return render_template(
                "admins/new_precinct.html", managers=managers, request=request
            )

        # TODO: Properlly lookup MANAGER once roles are configured
        manager = Users.query.filter_by(id=poll_manager_id).first()
        if manager is None:
            flash("No manager exists with the given ID")
            return render_template(
                "admins/new_precinct.html", managers=managers, request=request
            )

        zip_start_ranges = [v for k, v in request.form.items() if "zip-start-" in k]
        zip_end_ranges = [v for k, v in request.form.items() if "zip-end-" in k]
        if len(zip_start_ranges) < 1 or len(zip_end_ranges) < 1:
            flash("Please enter at least one zipcode range")
            return render_template(
                "admins/new_precinct.html", managers=managers, request=request
            )

        # validate the zip range values
        # TODO: Save the existing zipcodes so that they are not wiped in the form when an error is found
        zip_ranges = zip(zip_start_ranges, zip_end_ranges)
        for start, end in zip_ranges:
            if "-" in start:
                start = start.replace("-", "")
            if "-" in end:
                end = end.replace("-", "")
            start = int(start)
            end = int(end)
            if end < start:
                flash(
                    f"A zipcode range cannot have a end value of {end} that is less than it's start value of {start}"
                )
                return render_template(
                    "admins/new_precinct.html", managers=managers, request=request
                )
        # create the address
        # address validation
        if country.strip().upper() not in [
            "UNITED STATES",
            "US",
            "UNITED STATES OF AMERICA",
            "USA",
        ]:
            flash("Only United State residents may apply for registration")
            return render_template(
                "admins/new_precinct.html", managers=managers, request=request
            )

        address_verified, result = verify_address(
            ship_address, postcode, state, locality
        )
        if not address_verified:
            flash(result)
            return render_template(
                "admins/new_precinct.html", managers=managers, request=request
            )

        address = Address(
            ship_address, postcode, country, state, locality, apt_number=address2
        )
        db.session.add(address)
        db.session.commit()

        # create the precinct

        precinct = Precincts(precinct_name, phone_number, address.id, poll_manager_id)
        db.session.add(precinct)
        db.session.commit()

        # create the zip-ranges
        zip_ranges = zip(zip_start_ranges, zip_end_ranges)
        for start, end in zip_ranges:
            if "-" in start:
                start = start.replace("-", "")
            if "-" in end:
                end = end.replace("-", "")
            start = int(start)
            print("start2: ", start)
            end = int(end)
            zip_range = ZipRanges(start, end, precinct.id)
            db.session.add(zip_range)
            db.session.commit()

        flash(f"Precinct {precinct.name} was successfully created")
        return redirect(url_for("auth.profile"))

    return render_template("admins/new_precinct.html", managers=managers)
@admins.route("/search_user", methods=("GET", "POST"))
def search_user():

    if request.method == "POST":
        addresses = []
        username = request.form["username"]
        email = request.form["e-mail"]
        first_name = request.form["first"]
        last_name = request.form["last"]
        precinct = request.form["precinct"]
        zipcode = request.form["zipcode"]
        city = request.form["city"]
        state = request.form["state"]

        users = Users.query.all()
        searched_users = []

        if username != "":
            for user in users:
                if username.lower() == (user.username).lower() and username != "":
                    searched_users.append(user)
            users = searched_users
            searched_users = []

        if email != "":
            for user in users:
                if email.lower() == (user.email).lower() and email != "":
                    searched_users.append(user)
            users = searched_users
            searched_users = []

        if first_name != "":
            for user in users:
                if (user.first_name).lower() == first_name.lower() and first_name != "":
                    searched_users.append(user)
            users = searched_users
            searched_users = []

        if last_name != "":
            for user in users:
                if (user.last_name).lower() == last_name.lower() and last_name != "":
                    searched_users.append(user)
            users = searched_users
            searched_users = []

        if precinct != "":
            start_zip = ZipRanges.query.filter_by(precinct_id=precinct).first().start_zip_code
            end_zip = ZipRanges.query.filter_by(precinct_id=precinct).first().end_zip_code
            for user in users:
                user_zip = int(Address.query.filter_by(id=user.address_id).first().zip_code + "0000")
                if user_zip >= start_zip and user_zip <= end_zip:
                    searched_users.append(user)
            users = searched_users
            searched_users = []

        if zipcode != "":
            for user in users:
                if Address.query.filter_by(id=user.address_id).first().zip_code == zipcode and zipcode != "":
                    searched_users.append(user)
            users = searched_users
            searched_users = []

        if city != "":
            for user in users:
                if Address.query.filter_by(id=user.address_id).first().city == city and city != "":
                    searched_users.append(user)
            users = searched_users
            searched_users = []

        if state != "":
            for user in users:
                if Address.query.filter_by(id=user.address_id).first().state == state and state != "":
                    searched_users.append(user)
            users = searched_users

        for user in users:
            if user.username == "admin":
                users.remove(user)

        precincts = []
        for user in users:
            addresses.append(Address.query.filter_by(id=(user.address_id)).first())
            user_zip = int(Address.query.filter_by(id=user.address_id).first().zip_code + "0000")
            for precinct in ZipRanges.query.all():
                start_zip = precinct.start_zip_code
                end_zip = precinct.end_zip_code
                if user_zip >= start_zip and user_zip <= end_zip:
                    precincts.append(precinct.precinct_id)
        users_precincts = zip(users, precincts)

        return render_template("admins/search_results.html", users=users_precincts, addresses=addresses)

    return render_template("admins/search_user.html")

@admins.route("/create_ballot",methods=("GET", "POST"))
def create_ballot():

    if request.method == "POST":
        precinct = request.form.get("precinct")

        elections = ElectionsMock.query.filter_by(precinct_id=precinct)
        races = []
        for election in elections:
            races = races + RacesMock.query.filter_by(election_id=election.id).all()
        canidates = []
        for race in races:
            canidates = canidates + [CanidateMock.query.filter_by(id=race.canidate_1_id).first()] + [CanidateMock.query.filter_by(id=race.canidate_2_id).first()]
        for election in elections:
            ballot = Ballot(
                election_id=election.id,
                precinct_id=precinct,
            )
            db.session.add(ballot)
        db.session.commit()
        return render_template("admins/created_ballot.html", elections=elections, races=races, canidates=canidates)
    return render_template("admins/create_ballot.html")