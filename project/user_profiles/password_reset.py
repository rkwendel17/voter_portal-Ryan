import re

import pyotp
from werkzeug.security import generate_password_hash

from project.models import db
from werkzeug.exceptions import abort  # allows for 404 not found responses
from flask import redirect, render_template, request, Blueprint, flash, url_for
from project.general.models import Users
from flask import current_app
import yagmail

from project.user_profiles.models import (
    SecurityAnswers,
    EmailVerifications, SecurityQuestions

)

password_reset: Blueprint = Blueprint(
    "password_reset",
    __name__,
    template_folder="templates",
    static_folder="static",
)


def get_user(user_id) -> Users:
    user = Users.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return user


def get_security_answers(user_id) -> [SecurityAnswers]:
    answers = SecurityAnswers.query.filter_by(user_id=user_id).all()
    if answers is None or len(answers) == 0:
        abort(404)
    return answers


def send_email(recipient, subject, message):
    sender = current_app.config["EMAIL"]
    receiver = recipient
    subject = subject
    body = message

    yag = yagmail.SMTP(sender)
    yag.send(to=receiver, subject=subject, contents=body)


def email_verification_exists(user_id) -> bool:
    verification = EmailVerifications.query.filter_by(user_id=user_id).first()
    if verification is None:
        return False
    return True


def get_email_verification(user_id) -> EmailVerifications:
    verification = EmailVerifications.query.filter_by(user_id=user_id).first()
    if verification is None:
        abort(404)
    return verification


@password_reset.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":

        username = request.form.get("username")

        user = Users.query.filter_by(username=username).first()
        if user:
            if user.email_verified == False:
                flash("Please confirm your email.")
            elif user.registration_approved == False:
                flash("User pending approval, please try again later.")
            else:
                return redirect(url_for("password_reset.email_verification_reset", id=user.id))
        else:
            flash("Please check your username.")
        return render_template("password_reset/reset.html")

    else:
        return render_template("password_reset/reset.html")


@password_reset.route("/email_verification_reset/<int:id>", methods=("GET", "POST"))
def email_verification_reset(id):
    user = get_user(id)
    resend = request.args.get("resend", None) == "True"

    if request.method == "POST":
        submitted_code = request.form["code"]
        verification = get_email_verification(id)

        if submitted_code == verification.verification_code:
            user.email_verified = True
            db.session.delete(verification)
            db.session.commit()
            return redirect(url_for("password_reset.security_questions_answer", id=user.id))

        else:
            flash("Invalid verification code, please try again.")
            return render_template("password_reset/email_confirm_reset.html", user=user)

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
        f"   Our records indicate that you have recently opted to reset your\n"
        f"password for the United States Voter Portal. If this is correct,  \n"
        f"please use the code below. If this is wrong, please ignore this   \n"
        f"email and take no action.                                         \n"
        f"   Verification Code: {one_time_password}                         \n",
    )

    return render_template("password_reset/email_confirm_reset.html", user=user)


@password_reset.route("/security_questions_answer/<int:id>", methods=("GET", "POST"))
def security_questions_answer(id):
    answers = get_security_answers(id)
    id_answers = [answers[0].security_question_id, answers[1].security_question_id, answers[2].security_question_id]
    questions = [SecurityQuestions.query.filter_by(id=id_answers[0]).first(),
                 SecurityQuestions.query.filter_by(id=id_answers[1]).first(),
                 SecurityQuestions.query.filter_by(id=id_answers[2]).first()]

    if request.method == "POST":
        question_1 = request.form["question_1"]
        answer_1 = request.form["answer_1"]
        if answer_1.lower() == answers[0].answer.lower() and question_1 == questions[0].text:
            return redirect(url_for("password_reset.new_password", id=id))
        elif answer_1.lower() == answers[1].answer.lower() and question_1 == questions[1].text:
            return redirect(url_for("password_reset.new_password", id=id))
        elif answer_1.lower() == answers[2].answer.lower() and question_1 == questions[2].text:
            return redirect(url_for("password_reset.new_password", id=id))
        else:
            flash("Wrong answer, please try again.")
        return render_template("password_reset/security_questions_answer.html", answers=answers, questions=questions,
                           id_answers=id_answers)

    return render_template("password_reset/security_questions_answer.html", answers=answers, questions=questions,
                           id_answers=id_answers)

@password_reset.route("/new_password/<int:id>", methods=("GET", "POST"))
def new_password(id):
    user = get_user(id)

    if request.method == "POST":
        password = request.form["password"]

        if len(password) < 9:
            flash("Your password must be at least 10 characters long")
            return render_template("password_reset/new_password.html", user=user)

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
            return render_template("password_reset/new_password.html", user=user)

        user.password = generate_password_hash(password, method="sha256")
        db.session.commit()
        flash("Please login with your new credentials.")
        return redirect(url_for("general.home"))

    return render_template("password_reset/new_password.html", user=user)

