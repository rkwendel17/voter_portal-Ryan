import pytest
from unittest.mock import patch, Mock
from project.user_profiles.user_profiles import get_user, get_email_verification


def reset(test_client, username=None):
    response = test_client.post(
        "/reset",
        data={"username": username}
    )

    return response

def new_password(test_client, password="STRONGpassword123!@#"):
    response = test_client.post(
        "/new_password/<int:id>",
        data={"password": password}
    )

    return response

def test_valid_user(
        test_client, session, create_registered_user
):
    user, address = create_registered_user
    response = reset(test_client, user.username)
    print(response.data)
    assert response.location == "/email_verification_reset/1"

def test_invalid_user(
        test_client, session, create_registered_user
):
    user, address = create_registered_user
    response = reset(test_client, "invalid_username")
    print(response.data)
    assert b"Please check your username." in response.data
    assert b"Password Reset" in response.data

def test_user_pending_approval_reset(
        test_client, session, create_unregistered_user_with_verified_email
):
    user, address = create_unregistered_user_with_verified_email
    response = reset(test_client, user.username)
    print(response.data)
    assert b"User pending approval, please try again later." in response.data
    assert b"Password Reset" in response.data

def test_user_pending_email_reset(
        test_client, session, create_unregistered_user
):
    user, address = create_unregistered_user
    response = reset(test_client, user.username)
    print(response.data)
    assert b"Please confirm your email." in response.data
    assert b"Password Reset" in response.data

@patch("project.user_profiles.password_reset.send_email", Mock())
def test_get_email_verification_reset(test_client, session, create_unregistered_user):
    user = create_unregistered_user
    response = test_client.get("/email_verification_reset/1")
    verification = get_email_verification(1)
    assert verification.user_id == 1

@patch("project.user_profiles.password_reset.send_email", Mock())
def test_submit_email_verification_reset(test_client, session, create_unregistered_user):
    response = test_client.get("/email_verification_reset/1")
    user = get_user(1)
    assert user.email_verified == 0

    verification = get_email_verification(1)
    response = test_client.post(
        "/email_verification_reset/1", data={"code": verification.verification_code}
    )
    updated_user = get_user(1)
    assert updated_user.email_verified == 1

@patch("project.user_profiles.password_reset.send_email", Mock())
def test_submit_invalid_email_verification(
    test_client, session, create_unregistered_user
):
    response = test_client.get("/email_verification_reset/1")

    verification = get_email_verification(1)
    response = test_client.post("/email_verification_reset/1", data={"code": "notarealcode"})
    assert b"Invalid verification code, please try again." in response.data
    assert (
        b"Password reset in progress..." in response.data
    )

