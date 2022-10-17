# TODO: the contents of this file should be added to the database on startup.
import os

from werkzeug.security import generate_password_hash
from project.admins.models import ElectionsMock, RacesMock, CanidateMock

from project.general.models import Users
from project.user_profiles.models import SecurityQuestions, Address


def seed(db):
    # Seed security question options #########################################################
    db.session.add(SecurityQuestions("What was the name of your first pet?"))
    db.session.add(
        SecurityQuestions("What was the street address of your childhood home?")
    )
    db.session.add(SecurityQuestions("What was your mother's maiden name?"))
    db.session.add(
        SecurityQuestions("How old were you when you bought your first car?")
    )
    db.session.add(SecurityQuestions("What is your favorite TV show?"))
    db.session.commit()
    ###########################################################################################

    # Seed admin test account #################################################################
    if os.environ["FLASK_ENV"] != "test":
        address = Address(
            "1235 test blvd.", "54321", "United States", "Iowa", "Iowa City", apt_number="51"
        )
        db.session.add(address)
        db.session.commit()  # must commit here so that the address is available for the user below

        user = Users(
            username = "admin",
            email = "admin@admin.com",
            password = generate_password_hash("password", method="sha256"),
            first_name = "admin",
            last_name = "admin",
            address_id = address.id,
            dln = "12-34-56-78",
            ssn = "1234")

        election1 = ElectionsMock(
            name="President",
            date="04/22/2022",
            precinct_id=1
        )
        election2 = ElectionsMock(
            name="Vice President",
            date="04/22/2022",
            precinct_id=1
        )
        canidate1 = CanidateMock(
            name="Donald Trump"
        )
        canidate2 = CanidateMock(
            name="Joe Biden"
        )
        canidate3 = CanidateMock(
            name="Mike Pence"
        )
        canidate4 = CanidateMock(
            name="Kamela Harris"
        )
        race1 = RacesMock(
            election_id=1,
            canidate_1_id=1,
            canidate_2_id=2
        )
        race2 = RacesMock(
            election_id=2,
            canidate_1_id=3,
            canidate_2_id=4
        )
        user.email_verified = True
        user.registration_approved = True
        db.session.add(user)
        db.session.add(election1)
        db.session.add(election2)
        db.session.add(canidate1)
        db.session.add(canidate2)
        db.session.add(canidate3)
        db.session.add(canidate4)
        db.session.add(race1)
        db.session.add(race2)
        db.session.commit()
    ###########################################################################################



