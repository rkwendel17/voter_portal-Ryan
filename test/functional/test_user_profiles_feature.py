from unittest.mock import patch
from project.user_profiles.models import SecurityAnswers
from project.user_profiles.user_profiles import get_user, get_email_verification
from unittest.mock import Mock


# https://testdriven.io/blog/flask-pytest/


def register(
    test_client,
    first_name="first",
    middle_name="middle",
    last_name="last",
    username="username",
    password="STRONGpassword123!@#",
    email="email@gmail.com",
    dln="12-34-56-78",
    ssn="1234",
    ship_address="123 street address",
    address2="apt3",
    locality="Iowa City",
    state="Iowa",
    postcode="52240",
    country="USA",
):
    response = test_client.post(
        "/register",
        data={
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "username": username,
            "password": password,
            "email": email,
            "license": dln,
            "social": ssn,
            "ship-address": ship_address,
            "address2": address2,
            "locality": locality,
            "state": state,
            "postcode": postcode,
            "country": country,
        },
    )
    return response


def test_password_encryption(test_client, session):
    """Create a DB entry of user through the Site. Confirm that
    the password in the database is not equal to the string
    that was set as the password when created"""
    password = "aB1@password"
    response = register(test_client, password=password)
    user = get_user(1)
    assert user.password != password


def test_password_length_variant_one(test_client, session):
    """Variant 1: Go to the voter registration page. Fill out form.
    Enter a short password. Press submit. Ensure that the screen
    displays a flash stating that the password was insecurel;
    Variant 2:  Create password with proper length but no symbols.
    Variant 3: Create password with proper langth and
    symbols but no numbers."""
    response = register(test_client, password="12345")
    print(response.data)
    assert b"Your password must be at least 10 characters long" in response.data
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


def test_password_length_variant_two(test_client, session):
    """Variant 1: Go to the voter registration page. Fill out form.
    Enter a short password. Press submit. Ensure that the screen
    displays a flash stating that the password was insecurel;
    Variant 2:  Create password with proper length but no symbols.
    Variant 3: Create password with proper langth and
    symbols but no numbers."""
    response = register(test_client, password="1234567890")
    print(response.data)
    assert (
        b"Your password must contain an upper case letter, lower case letter, number, and symbol"
        in response.data
    )
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


def test_password_length_variant_three(test_client, session):
    """Variant 1: Go to the voter registration page. Fill out form.
    Enter a short password. Press submit. Ensure that the screen
    displays a flash stating that the password was insecurel;
    Variant 2:  Create password with proper length but no symbols.
    Variant 3: Create password with proper length and
    symbols but no numbers."""
    response = register(test_client, password="1234567890&")
    print(response.data)
    assert (
        b"Your password must contain an upper case letter, lower case letter, number, and symbol"
        in response.data
    )
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


def test_email_validation(test_client, session):
    """Variant 1: Go to voter registration page. Fil out user form enter
    email that does not conform to validation constraints. Verify that
    a error flash is displayed on submit and that the screen does
    not proceed to the next page."""
    response = register(test_client, email="notanemail")
    assert b"Please enter a valid email address" in response.data
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


def test_address_validation(test_client, session):
    """Variant 1: Go to voter registration page. Fil out user form enter
    email that does not conform to validation constraints. Verify that
    a error flash is displayed on submit and that the screen does
    not proceed to the next page."""
    response = register(test_client, state="notastate")
    assert (
        b"The following issues were found when validating your address:\n\tField &#39;State&#39; is invalid\n"
        in response.data
    )
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


def test_dln_validation(test_client, session):
    """Variant 1: Go to voter registration page. Fil out user form enter
    email that does not conform to validation constraints. Verify that
    a error flash is displayed on submit and that the screen does
    not proceed to the next page."""
    response = register(test_client, dln="notadln")
    assert b"Please enter a valid drivers license" in response.data
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


def test_ssn_validation(test_client, session):
    """Variant 1: Go to voter registration page. Fil out user form enter
    email that does not conform to validation constraints. Verify that
    a error flash is displayed on submit and that the screen does
    not proceed to the next page."""
    response = register(test_client, ssn="notassn")
    assert b"Please enter a valid Social Security Number" in response.data
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


@patch("project.user_profiles.user_profiles.send_email", Mock())
def test_get_email_verification(test_client, session, create_unregistered_user):
    user = create_unregistered_user
    response = test_client.get("/email_verification/1")
    verification = get_email_verification(1)
    assert verification.user_id == 1


@patch("project.user_profiles.user_profiles.send_email", Mock())
def test_submit_email_verification(test_client, session, create_unregistered_user):
    response = test_client.get("/email_verification/1")
    user = get_user(1)
    assert user.email_verified == 0

    verification = get_email_verification(1)
    response = test_client.post(
        "/email_verification/1", data={"code": verification.verification_code}
    )
    updated_user = get_user(1)
    assert updated_user.email_verified == 1


@patch("project.user_profiles.user_profiles.send_email", Mock())
def test_submit_invalid_email_verification(
    test_client, session, create_unregistered_user
):
    response = test_client.get("/email_verification/1")

    verification = get_email_verification(1)
    response = test_client.post("/email_verification/1", data={"code": "notarealcode"})
    assert b"invalid verification code, please try again." in response.data
    assert (
        b"Thank you for registering!" in response.data
    )  # to ensure we remained on the register page


def test_security_answers(test_client, session, create_unregistered_user):
    response = test_client.post(
        "/security_questions/1",
        data={
            "question_1": "1",
            "answer_1": "answer 1",
            "question_2": "2",
            "answer_2": "answer 2",
            "question_3": "3",
            "answer_3": "answer 3",
        },
    )
    answers = SecurityAnswers.query.all()
    assert answers[0].security_question_id == 1
    assert answers[0].answer == "answer 1"
    assert answers[1].security_question_id == 2
    assert answers[1].answer == "answer 2"
    assert answers[2].security_question_id == 3
    assert answers[2].answer == "answer 3"


def test_user_double_registration(test_client, session):
    """Create a DB entry of user through the Site. Confirm that
    the password in the database is not equal to the string
    that was set as the password when created"""
    register(
        test_client,
        username="kianv1",
        email="kianv1@gmail.com",
        dln="12-34-56-78",
        ssn="1234",
    )
    response = register(
        test_client,
        username="kianv2",
        email="totallynotthesamekian@gmail.com",
        dln="87-65-43-21",
        ssn="1234",
    )
    user = get_user(1)
    assert (
        b"Invalid submission, you have already registered. Please call our hotline for further assistance."
        in response.data
    )
    assert (
        b"Voter Registration" in response.data
    )  # to ensure we remained on the register page


def test_pin_generator(session, test_client, login):
    response = test_client.get("/create_user_pin")
    assert response.status_code == 200
    assert str.encode(f"pin") in response.data


def test_duplicate_pin_request(session, test_client, login):
    test_client.get("/create_user_pin")
    response = test_client.get("/create_user_pin")

    with test_client.session_transaction() as session:
        flash_message = dict(session["_flashes"]).get("danger")

    # Assert
    assert response.status_code == 200
    assert flash_message is not None
    assert (
        "A PIN has already been created for your account. Contact support for further assistance."
        == flash_message
    )
