from datetime import datetime
from project.models import db


class Precincts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)

    address_id = db.Column(db.Integer, db.ForeignKey("address.id"), nullable=False)
    address = db.relationship("Address", backref=db.backref("precincts", lazy=True))

    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    manager = db.relationship("Users", backref=db.backref("precincts", lazy=True))

    def __init__(
        self,
        name,
        phone_number,
        address_id,
        manager_id,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.phone_number = phone_number
        self.address_id = address_id
        self.manager_id = manager_id

    def __repr__(self):
        return (
            f"Precinct Name: {self.name}\n"
            f"Phone Number: {self.phone_number}\n"
            f"Address ID: {self.address_id}\n"
            f"Manager ID: {self.manager_id}\n"
        )


class ZipRanges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    start_zip_code = db.Column(db.Integer, nullable=False)
    end_zip_code = db.Column(db.Integer, nullable=False)

    precinct_id = db.Column(db.Integer, db.ForeignKey("precincts.id"), nullable=False)
    precinct = db.relationship("Precincts", backref=db.backref("zip_ranges", lazy=True))

    def __init__(
        self,
        start_zip_code,
        end_zip_code,
        precinct_id,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.start_zip_code = start_zip_code
        self.end_zip_code = end_zip_code
        self.precinct_id = precinct_id

    def __repr__(self):
        return (
            f"First Zip: {self.start_zip_code}\n"
            f"Last Zip: {self.end_zip_code}\n"
            f"Precinct ID: {self.precinct_id}\n"
        )

class ElectionsMock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    precinct_id = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        name,
        date,
        precinct_id,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.date = date
        self.precinct_id = precinct_id

    def __repr__(self):
        return (
            f"Name: {self.start_zip_code}\n"
            f"Date: {self.end_zip_code}\n"
            f"Precinct ID: {self.precinct_id}\n"
        )
        
class RacesMock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, nullable=False)
    canidate_1_id = db.Column(db.Integer, nullable=False)
    canidate_2_id = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        election_id,
        canidate_1_id,
        canidate_2_id,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.election_id = election_id
        self.canidate_1_id = canidate_1_id
        self.canidate_2_id = canidate_2_id

    def __repr__(self):
        return (
            f"Election: {self.election_id}\n"
            f"Canidate 1: {self.canidate_1_id}\n"
            f"Canidate 2: {self.canidate_2_id}\n"
        )

class CanidateMock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(
        self,
        name,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name


    def __repr__(self):
        return (
            f"Name: {self.name}\n"
        )

class Ballot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, nullable=False)
    precinct_id = db.Column(db.Integer, nullable=False)

    def __init__(
            self,
            election_id,
            precinct_id,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.election_id = election_id
        self.precinct_id = precinct_id

    def __repr__(self):
        return (
            f"Election id: {self.election_id}\n"
            f"Precinct ID: {self.precinct_id}\n"
        )

