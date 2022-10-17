from flask import Flask
from flask_login import LoginManager


def create_app():

    app = Flask(__name__)
    app.config.from_envvar("APPLICATION_SETTINGS")

    from project.models import db

    db.init_app(app)

    from project.general.models import Users

    login_manager = LoginManager()
    # View to redirect to when user needs to login
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    from project.general.general import general
    from project.user_profiles.user_profiles import user_profiles
    from project.user_profiles.auth import auth
    from project.admins.admins import admins
    from project.user_profiles.password_reset import password_reset

    app.register_blueprint(general)
    app.register_blueprint(user_profiles)
    app.register_blueprint(admins)
    app.register_blueprint(auth)
    app.register_blueprint(password_reset)

    return app
