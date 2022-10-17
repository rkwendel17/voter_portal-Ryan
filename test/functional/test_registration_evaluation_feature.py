import pytest
from project.user_profiles.user_profiles import get_user, get_email_verification


def test_pending_registration_index(
    session, test_client, create_unregistered_user_with_verified_email
):
    """Ensure that there is at least one pending registration. Make get request for users page, verify both the
    status code and the content of the page."""
    user, address = create_unregistered_user_with_verified_email
    response = test_client.get("/pending_registrations")
    print(str(response.data))

    assert response.status_code == 200
    assert "Pending Registrations" in str(response.data)
    assert user.first_name in str(response.data)
    assert user.last_name in str(response.data)
    assert str.encode(address.state) in response.data
    assert str.encode(address.city) in response.data
    assert str.encode(address.zip_code) in response.data


def test_pending_registration_index_none_submitted(session, test_client):
    """Ensure that there is at least one pending registration. Make get request for users page, verify both the
    status code and the content of the page."""
    response = test_client.get("/pending_registrations")

    assert response.status_code == 200
    assert b"Pending Registrations" in response.data
    assert b"There are no pending registrations at this time" in response.data


def test_pending_registration_show(
    session, test_client, create_unregistered_user_with_verified_email
):
    """Ensure that there is at least one pending registration. Make get request for users page, verify both the
    status code and the content of the page."""
    user, address = create_unregistered_user_with_verified_email
    response = test_client.get(f"/verify_registration/{user.id}")

    assert response.status_code == 200
    assert b"Pending Registration" in response.data
    assert str.encode(user.first_name) in response.data
    assert str.encode(user.middle_name) in response.data
    assert str.encode(user.last_name) in response.data
    assert str.encode(user.ssn) in response.data
    assert str.encode(user.dln) in response.data
    assert str.encode(user.email) in response.data


def test_pending_registration_error_invalid_id(session, test_client):
    """Ensure that there are no pending registrations. Go to a user registration show page for a random
    user id. Verify that you are redirected and that a flash error message is displayed"""
    response = test_client.get(f"/verify_registration/12")

    assert response.status_code == 404


def test_registration_approval(
    session, test_client, create_unregistered_user_with_verified_email, mocker
):
    """Ensure that there is at least one pending registration. Make a post to the registration approval route.
    Verify that a success message is displayed, a redirect occurs, and that the user's
    registration status is updated in the database."""
    mocked_email = mocker.patch("project.user_profiles.user_profiles.send_email")
    user, address = create_unregistered_user_with_verified_email
    response = test_client.post(f"/register/approve/{user.id}", follow_redirects=True)
    print(response.data)

    assert response.status_code == 200
    assert (
        str.encode(f"Registration for user {user.first_name} {user.last_name} approved")
        in response.data
    )


def test_registration_approval_email(
    session, test_client, create_unregistered_user_with_verified_email, mocker
):
    """Ensure that there is at least one pending registration. Make a post to the registration
    approval route. Confirm that the mocked email function is called with a success message."""
    mocked_email = mocker.patch("project.user_profiles.user_profiles.send_email")
    user, address = create_unregistered_user_with_verified_email
    response = test_client.post(f"/register/approve/{user.id}", follow_redirects=True)

    mocked_email.assert_called_with(
        user.email,
        f"Voter Registration Approved",
        f"Congrats {user.first_name} {user.last_name}!\n"
        f"Your voter registration has been approved.\n"
        f"You may now sign-in to the site with username and password specified at registration.\n"
        f"\tUsername: {user.username}\n"
        f"\tClick here to sign-in: http://127.0.0.1:8000/login\n",
    )


def test_registration_denial(
    session, test_client, create_unregistered_user_with_verified_email, mocker
):
    """Ensure that there is at least one pending registration. Make a post request to the reqistration denial route.
    Ensure that a success message is displayed (for the admin), that the admin is redirected,
    and the the user registration is removed from the database. (removal allows the user to
    attempt registration again with the same credentials)"""
    mocked_email = mocker.patch("project.user_profiles.user_profiles.send_email")
    user, address = create_unregistered_user_with_verified_email
    response = test_client.post(f"/register/deny/{user.id}", follow_redirects=True)

    with pytest.raises(Exception) as e:
        get_user(user.id)
        assert "404 Not Found" in e.value


def test_registration_denial_email(
    session, test_client, create_unregistered_user_with_verified_email, mocker
):
    """Ensure that there is at least one pending registration. Make a post to the registration
    denial route. Confirm that the mocked email function is called with a denial message."""
    mocked_email = mocker.patch("project.user_profiles.user_profiles.send_email")
    user, address = create_unregistered_user_with_verified_email
    response = test_client.post(f"/register/deny/{user.id}", follow_redirects=True)

    mocked_email.assert_called_with(
        user.email,
        f"Voter Registration Rejection",
        f"Sorry {user.first_name} {user.last_name},\n"
        f"Your voter registration wan NOT approved.\n"
        f"You will not be able to sign on to the site or use the online voter portal.\n"
        f"If you think this was a mistake, feel free to try again.\n"
        f"Want Help? Call our hotline 123-456-7890\n",
    )
