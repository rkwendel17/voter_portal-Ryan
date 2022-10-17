from datetime import datetime
from project.models import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # TODO - Set validations for roles
    role = db.Column(db.String(1), nullable=False, default="u")

    password = db.Column(db.String(100))

    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=False, default="")
    last_name = db.Column(db.String(100), nullable=False)

    address_id = db.Column(db.Integer, db.ForeignKey("address.id"), nullable=False)
    address = db.relationship("Address", backref=db.backref("users", lazy=True))

    dln = db.Column(db.String(20), nullable=False, unique=True)
    ssn = db.Column(db.String(20), nullable=False, unique=True)

    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    registration_approved = db.Column(db.Boolean, default=False, nullable=False)

    has_pin = db.Column(db.Boolean, default=False, nullable=False)

    users_security_answers = db.relationship("SecurityAnswers")

    def __init__(
        self,
        username,
        email,
        first_name,
        last_name,
        address_id,
        dln,
        ssn,
        middle_name=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address_id = address_id
        self.dln = dln
        self.ssn = ssn
        if middle_name is not None:
            self.middle_name = middle_name

    def __repr__(self):
        return (
            f"Username: {self.username}\n"
            f"Email: {self.email}\n"
            f"First Name: {self.first_name}\n"
            f"Middle Name: {self.middle_name}\n"
            f"Last Name: {self.last_name}\n"
            f"Address ID: {self.address_id}\n"
            f"DLN: {self.dln}\n"
            f"SSN: {self.ssn}\n"
            f"Email Verified: {self.email_verified}\n"
            f"Registration Approved: {self.registration_approved}\n"
        )

    def set_password(self, password):
        self.password = generate_password_hash(password, method="sha256")

    def set_role(self, role="u"):
        assert len(role) == 1
        self.role = role.lower()

    def is_email_verified(self):
        return self.email_verified

    def is_approved(self):
        assert self.is_email_verified()
        return self.registration_approved

    def verify_password(self, password):
        return check_password_hash(self.password, password)
