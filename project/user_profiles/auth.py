from flask import redirect, render_template, request, Blueprint, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from project.general.models import Users

auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember", False)

        user = Users.query.filter_by(username=username).first()
        if user:
            if not user.is_email_verified():
                flash("Please confirm your email")
                return render_template("auth/login.html")
            elif not user.is_approved():
                flash("User pending approval, please try again later")
                return render_template("auth/login.html")
            else:
                if user.verify_password(password):
                    flash("Login successful")
                    login_user(user, remember=remember)
                    return redirect(url_for("auth.profile"))
                else:
                    flash("Please check your username or password")
                    return render_template("auth/login.html")
        else:
            flash("Please check your username or password")
            return render_template("auth/login.html")

    else:
        return render_template("auth/login.html")


@auth.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html", name=current_user.username)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("general.home"))
