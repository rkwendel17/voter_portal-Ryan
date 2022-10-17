import random
import re

import pyotp

from sqlalchemy.exc import IntegrityError
from flask import Blueprint

from project.models import db
from flask import render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort  # allows for 404 not found responses
from project.general.models import Users
from project.general.general import ROWS_PER_PAGE
from flask_login import login_required, current_user

from project.user_profiles.models import (
    Address,
    SecurityQuestions,
    SecurityAnswers,
    EmailVerifications,
    SecretVote,
    UserVoteStatus,
)
from flask import current_app
import yagmail

# TODO: Convert all URLs to url_for's
# TODO: resolve DB injection security issues

user_profiles = Blueprint(
    "user_profiles",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/user_profiles",
)

MINIMUM_CODE_DIGITS = 6

def get_user(user_id) -> Users:
    user = Users.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return user


def get_pending_users(page=None) -> [Users]:
    if page is None:
        users = Users.query.filter_by(
            registration_approved=False, email_verified=True
        ).all()
        if users is None or len(users) == 0:
            return []
    else:
        users = Users.query.filter_by(
            registration_approved=False, email_verified=True
        ).paginate(page=page, per_page=ROWS_PER_PAGE)

    return users


# TODO: !!!!!! Update this to only retrieve managers once roles are implemented !!!!!! TODO
def get_managers() -> [Users]:
    users = Users.query.all()
    if users is None or len(users) == 0:
        return []
    return users


def get_security_answers(user_id) -> [SecurityAnswers]:
    answers = SecurityAnswers.query.filter_by(user_id=user_id).all()
    if answers is None or len(answers) == 0:
        abort(404)
    return answers


def get_email_verification(user_id) -> EmailVerifications:
    verification = EmailVerifications.query.filter_by(user_id=user_id).first()
    if verification is None:
        abort(404)
    return verification


def delete_user(user: Users):
    SecurityAnswers.query.filter_by(user_id=user.id).delete()
    EmailVerifications.query.filter_by(user_id=user.id).delete()
    Users.query.filter_by(id=user.id).delete()
    return


def email_verification_exists(user_id) -> bool:
    verification = EmailVerifications.query.filter_by(user_id=user_id).first()
    if verification is None:
        return False
    return True


def get_election_races(election_id, page=None):
    # Here is where we should query the races database
    # Based on the election, precinct, and date. This is stubbed for now.
    if page is None:
        # GET ALL RACES
        pass
    else:
        # GET FIRST PAGE OF RACES
        pass

    return [{"Name": "President", "Date": "04/22/2022", "id": 1},
            {"Name": "Vice President", "Date": "04/22/2022", "id": 2}]


def get_current_election_id():
    # Assuming only one election per day (In each region). The election may have as many races as necessary
    # This is stubbed until the previous functionality is introduced
    return 1


def get_election(id):
    # Get an election by id
    return {"Title": "ELECTION TITLE", "Date": "04/22/2022", "id": 1}


def get_user_votes_for_election(election_id, pin):
    # Not paginated to allow for printing
    races = get_election_races(election_id=election_id)
    race_ids = [race["id"] for race in races]

    votes = []
    for race_id in race_ids:
        user_vote = SecretVote.query.filter_by(
            race_id=race_id, pin=pin
        ).all()
        if user_vote:
            votes.append(user_vote[0])

    if votes is None or len(votes) == 0:
        return []

    return votes


def get_race_candidates(race_id, page=None):
    # Here is where we should query the candidate database
    # Based on the race. This is stubbed for now.
    if page is None:
        # GET ALL CANDIDATES
        pass
    else:
        # GET FIRST PAGE OF CANDIDATES
        pass

    return [{"Name": "Joe Biden", "id": 1},
            {"Name": "Donald Trump", "id": 2}]


def get_candidate(candidate_id) -> Users:
    # candidate = Candidates.query.filter_by(id=candidate_id).first()
    candidate = {"image": "https://cdn.vox-cdn.com/thumbor/rhZpM6DYZlh10boukPzM_ZBbv5w=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/19608331/1193798833.jpg.jpg",
                 "name": "Joe biden",
                 "age": 79,
                 "description": "Joseph Robinette Biden Jr. is an American politician who is the 46th and current president of the United States. A member of the Democratic Party, he served as the 47th vice president from 2009 to 2017 under Barack Obama and represented Delaware in the United States Senate from 1973 to 2009.",
                 "race":  # The race will be an object in the real implementation (referenced by foreign key)
                    {"title": "Presidential",
                     "id": 1}}
    if candidate is None:
        abort(404)
    return candidate


def get_race(race_id) -> Users:
    # race = Races.query.filter_by(id=race_id).first()
    race = {"Name": "President", "Date": "04/22/2022", "id": 1}
    if race is None:
        abort(404)
    return race


def has_voted(user_id, race_id) -> bool:
    votes = UserVoteStatus.query.filter_by(user_id=user_id, race_id=race_id).all()
    return not (votes is None or len(votes) == 0)


def generate_unique_random_code(existing_codes: []):
    number_of_codes = len(existing_codes)
    digits = len(str(number_of_codes))
    if digits < MINIMUM_CODE_DIGITS:
        digits = MINIMUM_CODE_DIGITS

    # add a digit when the capacity exceeds 50%
    elif 10**digits <= number_of_codes:
        digits += 1

    existing_code_set = set(existing_codes)
    possible_code_set = set(range(10 ** (digits - 1), (10**digits)))
    valid_unique_codes = possible_code_set - existing_code_set

    number_of_choices = len(valid_unique_codes)
    code_index = random.randint(0, number_of_choices - 1)

    return list(valid_unique_codes)[code_index]


@user_profiles.route("/create_user_pin")
@login_required
def create_user_pin():
    user = current_user
    if user.has_pin:
        flash(f"A PIN has already been created for your account. Contact support for further assistance.", "danger")
        return {"pin": ""}

    votes = SecretVote.query.all()
    pins = [v.pin for v in votes if v != ""]
    pin = generate_unique_random_code(pins)

    user = get_user(user.id)
    user.has_pin = True
    db.session.commit()

    return {"pin": pin}


@user_profiles.route("/races")
@login_required
def races():
    page = request.args.get("page", 1, type=int)

    current_election_id = get_current_election_id()

    election_races = get_election_races(current_election_id, page=page)

    all_votes_submitted = True

    vote_map = {}
    for race in election_races:
        vote_map[race["id"]] = has_voted(current_user.id, race["id"])
        if not has_voted(current_user.id, race["id"]):
            all_votes_submitted = False

    # note: When the stubbed functions are fixed we may need to
    # update some of the formatting in the HTML file
    if all_votes_submitted:
        return redirect(url_for("user_profiles.voter_summary", election_id=current_election_id))
    else:
        return render_template("user_profiles/races_index.html",
                               races=election_races,
                               vote_map=vote_map,
                               election_id=current_election_id)


@user_profiles.route("/candidates/<int:race_id>")
@login_required
def candidates(race_id):
    if has_voted(current_user.id, race_id):
        flash(f"You have already voted for this race", "info")
        return redirect(url_for("user_profiles.races"))

    page = request.args.get("page", 1, type=int)
    race_candidates = get_race_candidates(race_id, page=page)
    race = get_race(race_id)
    # note: When the stubbed functions are fixed we may need to
    # update some of the formatting in the HTML file
    return render_template("user_profiles/candidates_index.html", race_candidates=race_candidates, race=race)


@user_profiles.route("/candidate/<int:id>")
@login_required
def candidate(id):
    candidate = get_candidate(id)
    # note: When the stubbed functions are fixed we may need to
    # update some of the formatting in the HTML file
    return render_template("user_profiles/candidate.html", candidate=candidate)


@user_profiles.route("/abstain/<int:race_id>", methods=("POST",))
@login_required
def abstain(race_id):
    if has_voted(current_user.id, race_id):
        flash(f"You have already voted for this race", "info")
        return redirect(url_for("user_profiles.races"))

    race = get_race(race_id)

    flash(f"You have abstained from the following race: {race['Name']}", "info")

    user_vote = UserVoteStatus(current_user.id, race_id)
    db.session.add(user_vote)
    db.session.commit()
    # note: When the stubbed functions are fixed we may need to
    # update some of the formatting in the HTML file
    return redirect(url_for("user_profiles.races"))


@user_profiles.route("/vote/<int:race_id>", methods=("POST",))
@login_required
def vote(race_id):
    candidate_id = request.form["candidate_id"]
    pin = request.form["pin"]

    if has_voted(current_user.id, race_id):
        flash(f"You have already voted for this race", "info")
        return redirect(url_for("user_profiles.races"))

    candidate = get_candidate(candidate_id)
    race = get_race(race_id)

    if candidate_id:
        user_vote = UserVoteStatus(current_user.id, race_id)
        db.session.add(user_vote)
        db.session.commit()

        if pin != "MISSING":
            secret_vote = SecretVote(race_id, candidate_id, pin=pin)
        else:
            secret_vote = SecretVote(race_id, candidate_id)

        db.session.add(secret_vote)
        db.session.commit()

        flash(f"Vote successfully submitted for {race['Name']} {candidate['name']}", "info")
        # note: When the stubbed functions are fixed we may need to
        # update some of the formatting in the HTML file
        return redirect(url_for("user_profiles.races"))
    flash(f"Please select a candidate or abstain before voting", "info")
    return redirect(url_for("user_profiles.candidates", race_id=race_id))


@user_profiles.route("/summary/<int:election_id>")
@login_required
def voter_summary(election_id):
    pin = request.args.get('pin_input')
    results = get_user_votes_for_election(election_id, pin)
    return render_template("user_profiles/voter_summary.html", results=results, pin=pin, election=get_election(election_id))


@user_profiles.route("/register/approve/<int:id>", methods=("POST",))
def approve_registration(id):
    user = get_user(id)
    user.registration_approved = True
    db.session.commit()
    flash(f"Registration for user {user.first_name} {user.last_name} approved", "info")
    send_email(
        user.email,
        f"Voter Registration Approved",
        f"Congrats {user.first_name} {user.last_name}!\n"
        f"Your voter registration has been approved.\n"
        f"You may now sign-in to the site with username and password specified at registration.\n"
        f"\tUsername: {user.username}\n"
        f"\tClick here to sign-in: http://127.0.0.1:8000/login\n",
    )  # TODO: URL would change for deployment
    return redirect(url_for("admins.pending_registrations"))


@user_profiles.route("/register/deny/<int:id>", methods=("POST",))
def deny_registration(id):
    user = get_user(id)
    delete_user(user)
    db.session.commit()
    flash(f"Registration for user {user.first_name} {user.last_name} denied", "info")
    send_email(
        user.email,
        f"Voter Registration Rejection",
        f"Sorry {user.first_name} {user.last_name},\n"
        f"Your voter registration wan NOT approved.\n"
        f"You will not be able to sign on to the site or use the online voter portal.\n"
        f"If you think this was a mistake, feel free to try again.\n"
        f"Want Help? Call our hotline 123-456-7890\n",
    )
    return redirect(url_for("admins.pending_registrations"))


@user_profiles.route("/register/retry/<int:id>")
def retry_registration(id):
    # TODO: remember security question answers on resubmit
    user = get_user(id)

    # Prevent changes after verification
    if user.email_verified or user.registration_approved:
        abort(404)

    address = user.address
    delete_user(user)
    db.session.commit()
    return render_template("user_profiles/register.html", user=user, address=address)


@user_profiles.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        username = request.form["username"]
        password = request.form["password"]  # TODO: needs to be encrypted
        email = request.form["email"]
        dln = request.form["license"]
        ssn = request.form["social"]
        ship_address = request.form["ship-address"]
        address2 = request.form["address2"]
        locality = request.form["locality"]
        state = request.form["state"]
        postcode = request.form["postcode"]
        country = request.form["country"]

        required_fields = [
            first_name,
            last_name,
            username,
            password,
            email,
            dln,
            ssn,
            ship_address,
            locality,
            state,
            postcode,
        ]

        # basic validation
        if "" in required_fields:
            flash(
                "You are missing one or more required fields"
            )  # TODO: Could enhance error messages in the future
            return render_template("user_profiles/register.html")

        # password validation
        if len(password) < 9:
            flash("Your password must be at least 10 characters long")
            return render_template("user_profiles/register.html")

        # Theses a better way to do these regexes...
        if (
            not re.match(r".*[A-Z]+.*", password)
            or not re.match(r".*[a-z]+.*", password)
            or not re.match(r".*[0-9]+.*", password)
            or not re.match(r".*[^A-Za-z0-9]+.*", password)
        ):
            flash(
                "Your password must contain an upper case letter, lower case letter, number, and symbol"
            )
            return render_template("user_profiles/register.html")

        # Email validation
        if not re.fullmatch(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", email
        ):
            flash("Please enter a valid email address")
            return render_template("user_profiles/register.html")

        # dln validation
        if not re.fullmatch(r"\d\d-\d\d-\d\d-\d\d", dln):
            flash("Please enter a valid drivers license")
            return render_template("user_profiles/register.html")

        # ssn validation
        if not re.fullmatch(r"\d\d\d\d", ssn):
            flash("Please enter a valid Social Security Number")
            return render_template("user_profiles/register.html")

        # address validation
        if country.strip().upper() not in [
            "UNITED STATES",
            "US",
            "UNITED STATES OF AMERICA",
            "USA",
        ]:
            flash("Only United State residents may apply for registration")
            return render_template("user_profiles/register.html")

        address_verified, result = verify_address(
            ship_address, postcode, state, locality
        )
        if not address_verified:
            flash(result)
            return render_template("user_profiles/register.html")

        address = Address(
            ship_address, postcode, country, state, locality, apt_number=address2
        )
        db.session.add(address)
        db.session.commit()

        if Users.query.filter_by(username=username).first() is not None:
            flash(f"Username {username} is already taken. Please choose another.")
            return render_template("user_profiles/register.html")

        if Users.query.filter_by(email=email).first() is not None:
            flash(f"The email {email} is already registered with another user.")
            return render_template("user_profiles/register.html")

        if (
            Users.query.filter_by(dln=dln).first() is not None
            or Users.query.filter_by(ssn=ssn).first() is not None
        ):
            flash(
                f"Invalid submission, you have already registered. Please call our hotline for further assistance."
            )
            return render_template("user_profiles/register.html")

        try:
            user = Users(
                username,
                email,
                first_name,
                last_name,
                address.id,
                dln,
                ssn,
                middle_name=middle_name,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            subject = str(e.orig).strip("()\"'").split(".")[-1]
            flash(f"A user with this {subject} has already applied for registration.")
            return render_template("user_profiles/register.html")
        except Exception as e:
            flash(f"An error occurred. {e}")
            return render_template("user_profiles/register.html")

        return redirect(url_for("user_profiles.security_questions", id=user.id))

    return render_template("user_profiles/register.html", User={}, Address={})


@user_profiles.route("/security_questions/<int:id>", methods=("GET", "POST"))
def security_questions(id):
    user = get_user(id)
    questions = SecurityQuestions.query.all()

    if request.method == "POST":
        question_1 = request.form["question_1"]
        answer_1 = request.form["answer_1"]
        db.session.add(SecurityAnswers(id, question_1, answer_1))

        question_2 = request.form["question_2"]
        answer_2 = request.form["answer_2"]
        db.session.add(SecurityAnswers(id, question_2, answer_2))

        question_3 = request.form["question_3"]
        answer_3 = request.form["answer_3"]
        db.session.add(SecurityAnswers(id, question_3, answer_3))
        db.session.commit()
        return redirect(url_for("user_profiles.email_verification", id=id))

    return render_template(
        "user_profiles/security_questions.html", user=user, questions=questions
    )


@user_profiles.route("/email_verification/<int:id>", methods=("GET", "POST"))
def email_verification(id):
    user = get_user(id)
    resend = request.args.get("resend", None) == "True"

    if request.method == "POST":
        submitted_code = request.form["code"]
        verification = get_email_verification(id)

        if submitted_code == verification.verification_code:
            user.email_verified = True
            db.session.delete(verification)
            db.session.commit()
            return render_template("user_profiles/registration_success_screen.html")

        else:
            flash("invalid verification code, please try again.")
            return render_template("user_profiles/email_confirm.html", user=user)

    if not email_verification_exists(id) or resend:

        # delete old code if re-requesting
        if resend and email_verification_exists(id):
            verification = get_email_verification(id)
            db.session.delete(verification)
            db.session.commit()

        totp = pyotp.TOTP("base32secret3232")
        one_time_password = (
            totp.now()
        )  # TODO: Hash this password before saving to the DB

        email_verification_entry = EmailVerifications(id, one_time_password)
        db.session.add(email_verification_entry)
        db.session.commit()
        send_email(
            user.email,
            "Please verify your voter registration email",
            f"Hello {user.first_name} {user.middle_name} {user.last_name}, \n"
            f"\n"
            f"   Our records indicate that you have recently registered to \n"
            f"vote with the United States Voter Portal. If this is correct,\n"
            f"please use the code below. If this is wrong, please ignore   \n"
            f"this email and take no action.                               \n"
            f"   Verification Code: {one_time_password}                    \n",
        )

    return render_template("user_profiles/email_confirm.html", user=user)


def send_email(recipient, subject, message):
    sender = current_app.config["EMAIL"]
    receiver = recipient
    subject = subject
    body = message

    yag = yagmail.SMTP(sender)
    yag.send(to=receiver, subject=subject, contents=body)


@user_profiles.route("/registration_success_screen")
def registration_success_screen():
    return render_template("user_profiles/registration_success_screen.html")


def verify_address(ship_address, postcode, state, locality):
    """Only US addresses are supported (as it is an US voting system)"""
    # SOURCE: https://pypi.org/project/google-i18n-address/
    from i18naddress import InvalidAddress, normalize_address

    try:
        address = normalize_address(
            {
                "country_code": "US",
                "country_area": state,
                "city": locality,
                "postal_code": postcode,
                "street_address": ship_address,
            }
        )
        return True, address
    except InvalidAddress as e:
        error = "The following issues were found when validating your address:\n"
        for field, problem in e.errors.items():
            if field == "country_area":
                field = "state"
            field = field.replace("_", " ").capitalize()
            error += f"\tField '{field}' is {problem}\n"
        return False, error

    # TODO: May try to use geocoder in the future
    # from pygeocoder import Geocoder
    #
    # business_name = "99 Fake location, Iowa City IA, 52240"
    # print("Searching %s" % business_name)
    # results = Geocoder(api_key=current_app.config["API_KEY"]).geocode(business_name)
    # input(results)
