def login(test_client, username=None, password=None, remember=True):
    response = test_client.post(
        "/login",
        data={"username": username, "password": password, "remember": remember},
    )

    return response


def test_user_pending_email_verification(
    test_client, session, create_unregistered_user
):
    user, address = create_unregistered_user
    response = login(test_client, user.username, "STRONGpassword123!@#", True)
    print(response.data)
    assert b"Please confirm your email" in response.data


def test_user_pending_approval(
    test_client, session, create_unregistered_user_with_verified_email
):
    user, address = create_unregistered_user_with_verified_email
    response = login(test_client, user.username, "STRONGpassword123!@#", True)
    print(response.data)
    assert b"User pending approval, please try again later" in response.data


def test_valid_user_login_with_correct_credentials(
    test_client, session, create_registered_user
):
    user, address = create_registered_user
    response = login(test_client, user.username, "STRONGpassword123!@#", True)
    assert response.location == "/profile"


def test_valid_user_login_with_incorrect_credentials(
    test_client, session, create_registered_user
):
    user, address = create_registered_user
    response = login(test_client, user.username, "password!@#", True)
    assert b"Please check your username or password" in response.data


def test_invalid_user_login(test_client, session):
    response = login(test_client, "invalidName", "invalidPass", True)
    assert b"Please check your username or password" in response.data


def test_invalid_user_login_with_password(test_client, session):
    response = login(test_client, "invalidName", "STRONGpassword123!@#", True)
    assert b"Please check your username or password" in response.data


def test_empty_login_fields(test_client, session):
    response = login(test_client)
    assert b"Please check your username or password" in response.data


def test_login_after_password_update(test_client, session, create_registered_user):
    user, address = create_registered_user
    user.set_password("newPass123#$")
    response = login(test_client, user.username, "newPass123#$", True)
    assert response.location == "/profile"
