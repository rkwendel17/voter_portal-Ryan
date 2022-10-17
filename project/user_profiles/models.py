from datetime import datetime

from project.models import db

# Flask-Login provides easy user session management


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street_address = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(60), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    apt_number = db.Column(db.String(20))

    def __init__(
        self, street_address, zip_code, country, state, city, apt_number=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.street_address = street_address
        self.zip_code = zip_code
        self.country = country
        self.state = state
        self.city = city
        if apt_number is not None:
            self.apt_number = apt_number

    def __repr__(self):
        return "TODO: print address model"


class SecurityQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def __repr__(self):
        return "TODO: print security questions model"


class SecurityAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    security_answers_user = db.relationship(
        "Users", overlaps="user,users_security_answers"
    )

    security_question_id = db.Column(
        db.Integer, db.ForeignKey("security_questions.id"), nullable=False
    )
    security_question = db.relationship(
        "SecurityQuestions", backref=db.backref("security_answers", lazy=True)
    )

    answer = db.Column(db.String(300), nullable=False)

    def __init__(self, user_id, security_question_id, answer, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.security_question_id = security_question_id
        self.answer = answer

    def __repr__(self):
        return "TODO: print security answers model"


class EmailVerifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    unverified_user = db.relationship(
        "Users", backref=db.backref("email_verifications", lazy=True)
    )
    verification_code = db.Column(db.String(60), nullable=False)

    def __init__(self, user_id, verification_code, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.verification_code = verification_code

    def __repr__(self):
        return "TODO: print security answers model"


class SecretVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    race_id = db.Column(db.Integer)
    # race_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # race = db.relationship("Users", backref=db.backref("user_vote_status", lazy=True))

    candidate_id = db.Column(db.Integer)
    # candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    # candidate = db.relationship("Candidates", backref=db.backref("secret_vote", lazy=True))

    pin = db.Column(db.String(60), nullable=False)

    def __init__(self, race_id, candidate_id, pin="", **kwargs):
        super().__init__(**kwargs)
        self.race_id = race_id
        self.candidate_id = candidate_id
        self.pin = pin

    def __repr__(self):
        return "TODO: print user vote status model"


class UserVoteStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("Users", backref=db.backref("user_vote_status", lazy=True))

    race_id = db.Column(db.Integer)
    # race_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # race = db.relationship("Users", backref=db.backref("user_vote_status", lazy=True))

    def __init__(self, user_id, race_id, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.race_id = race_id

    def __repr__(self):
        return "TODO: print user vote status model"