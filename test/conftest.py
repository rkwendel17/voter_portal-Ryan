from urllib import response
from flask_login import login_user
import pytest as pytest
from app import create_app


# https://testdriven.io/blog/flask-pytest/
# Write all of your fixtures here
# Finally, fixtures can be run with different scopes:
#
# function - run once per test function (default scope)
# class - run once per test class
# module - run once per module (e.g., a test file)
# session - run once per session
from project.user_profiles.models import Address
from project.general.models import Users
from project.models import db as _db


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session")
def db(app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()

    _db.app = app

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="function")
def test_client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def create_address(session):
    address = Address(
        "street address", "12345", "US", "Iowa", "Iowa City", apt_number="1"
    )
    session.add(address)
    session.commit()
    return address


@pytest.fixture(scope="function")
def create_unregistered_user(session, create_address):
    address = create_address
    user = Users(
        username="username",
        email="email@gmail.com",
        first_name="first name",
        last_name="last name",
        address_id=address.id,
        dln="12-34-56-78",
        ssn="1234",
        middle_name="middle",
    )
    user.set_password("STRONGpassword123!@#")
    session.add(user)
    session.commit()
    return user, address


@pytest.fixture(scope="function")
def create_unregistered_user_with_verified_email(session, create_unregistered_user):
    user, address = create_unregistered_user
    user.email_verified = True
    session.add(user)
    session.commit()
    return user, address


@pytest.fixture(scope="function")
def create_registered_user(session, create_unregistered_user_with_verified_email):
    user, address = create_unregistered_user_with_verified_email
    user.registration_approved = True
    session.add(user)
    session.commit()
    return user, address


@pytest.fixture(scope="function")
def login(session, test_client, create_registered_user):
    user, address = create_registered_user
    response = test_client.post(
        "/login",
        data={
            "username": user.username,
            "password": "STRONGpassword123!@#",
            "remember": True,
        },
    )

    return user, address


@pytest.fixture(scope="function")
def vote(session, test_client, login, mocker):
    # Will require updates when databases are integrated
    mocker.patch("project.user_profiles.user_profiles.has_voted", return_value=False)
    mocker.patch(
        "project.user_profiles.user_profiles.get_candidate",
        return_value={
            "image": "https://cdn.vox-cdn.com/thumbor/rhZpM6DYZlh10boukPzM_ZBbv5w=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/19608331/1193798833.jpg.jpg",
            "name": "Joe Biden",
            "age": 79,
            "description": "Joseph Robinette Biden Jr. is an American politician who is the 46th and current president of the United States. A member of the Democratic Party, he served as the 47th vice president from 2009 to 2017 under Barack Obama and represented Delaware in the United States Senate from 1973 to 2009.",
            "race": {"title": "Presidential", "id": 1},
        },
    )
    mocker.patch(
        "project.user_profiles.user_profiles.get_race",
        return_value={"Name": "President", "Date": "04/22/2022", "id": 1},
    )

    pin = 123456

    test_client.post("/vote/1", data={"candidate_id": 1, "pin": pin})

    return pin
