from unittest.mock import patch, call
import project
from project.user_profiles.user_profiles import (
    send_email,
    generate_unique_random_code,
    MINIMUM_CODE_DIGITS,
    has_voted,
    get_user_votes_for_election
)


# https://testdriven.io/blog/flask-pytest/


def test_new_address(create_address):
    address = create_address
    assert address.street_address == "street address"
    assert address.zip_code == "12345"
    assert address.country == "US"
    assert address.state == "Iowa"
    assert address.city == "Iowa City"
    assert address.apt_number == "1"


def test_create_unregistered_user(create_unregistered_user):
    """Create DB entry through SQLAlchemy and user model. Ensure that
    the following fields are set as expected: First name, middle name,
    last name, Home address, zip code, country (should be US), state,
    city, apt #, username, email, DLN, SSN"""
    user, address = create_unregistered_user
    assert user.username == "username"
    assert user.email == "email@gmail.com"
    assert user.verify_password("STRONGpassword123!@#")
    assert user.first_name == "first name"
    assert user.last_name == "last name"
    assert user.dln == "12-34-56-78"
    assert user.ssn == "1234"
    assert user.middle_name == "middle"


def test_create_unregistered_user_with_verified_email(
    create_unregistered_user_with_verified_email,
):
    """Create DB entry through SQLAlchemy and user model. Ensure that
    the following fields are set as expected: First name, middle name,
    last name, Home address, zip code, country (should be US), state,
    city, apt #, username, email, DLN, SSN"""
    user, address = create_unregistered_user_with_verified_email
    assert user.username == "username"
    assert user.email == "email@gmail.com"
    assert user.verify_password("STRONGpassword123!@#")
    assert user.first_name == "first name"
    assert user.last_name == "last name"
    assert user.dln == "12-34-56-78"
    assert user.ssn == "1234"
    assert user.middle_name == "middle"
    assert user.email_verified == True


# SOURCE: https://docs.python.org/3/library/unittest.mock.html#patch-object
@patch.object(project.user_profiles.user_profiles.yagmail.SMTP, "send")
def test_send_email(mock_method):
    send_email("a", "b", "c")
    mock_method.assert_called_with(to="a", subject="b", contents="c")


def test_pin_code_generator():
    # generate a 6 digit code
    code = generate_unique_random_code([])
    assert len(str(code)) == 6

    # run twenty times to ensure no collisions occur when as full as possible
    codes = set(range(int(10**MINIMUM_CODE_DIGITS) - 20))
    for i in range(20):
        code = generate_unique_random_code(list(codes))
        assert len(str(code)) == 6
        assert code not in codes
        codes.add(code)

    # generate a 7 digit code when 50% capacity is surpassed
    codes = range(int(10**MINIMUM_CODE_DIGITS))
    code = generate_unique_random_code(codes)
    assert len(str(code)) == 7


# Mocked function format may need to change slightly once the real implementation is added
def test_races_index_page(session, test_client, login, mocker):
    mocker.patch(
        "project.user_profiles.user_profiles.get_current_election_id", return_value=1
    )
    mocked_get_election_races = mocker.patch(
        "project.user_profiles.user_profiles.get_election_races",
        return_value=[
            {"Name": "President", "Date": "04/22/2022", "id": 1},
            {"Name": "Vice President", "Date": "04/22/2022", "id": 2},
        ],
    )
    mocked_has_voted = mocker.patch(
        "project.user_profiles.user_profiles.has_voted", return_value=False
    )

    response = test_client.get("/races")

    mocked_get_election_races.assert_called_with(1, page=1)
    mocked_has_voted.assert_has_calls([call(1, 1), call(1, 2)])
    assert str.encode("President") in response.data
    assert str.encode("Vice President") in response.data


# Mocked function format may need to change slightly once the real implementation is added
def test_candidates_index_page(session, test_client, login, mocker):
    mocked_has_voted = mocker.patch(
        "project.user_profiles.user_profiles.has_voted", return_value=False
    )
    mocker.patch(
        "project.user_profiles.user_profiles.get_race",
        return_value={"Name": "President", "Date": "04/22/2022", "id": 1},
    )
    mocked_get_race_candidates = mocker.patch(
        "project.user_profiles.user_profiles.get_race_candidates",
        return_value=[
            {"Name": "Joe Biden", "id": 1},
            {"Name": "Donald Trump", "id": 2},
        ],
    )

    response = test_client.get("/candidates/1")

    mocked_has_voted.assert_called_with(1, 1)
    mocked_get_race_candidates.assert_called_with(1, page=1)
    assert str.encode("Joe Biden") in response.data
    assert str.encode("Donald Trump") in response.data


# Mocked function format may need to change slightly once the real implementation is added
def test_candidates_index_page_already_voted(session, test_client, login, mocker):
    mocked_has_voted = mocker.patch(
        "project.user_profiles.user_profiles.has_voted", return_value=True
    )

    response = test_client.get("/candidates/1")

    with test_client.session_transaction() as session:
        flash_message = dict(session["_flashes"]).get("info")

    # Assert
    assert response.status_code == 302
    assert flash_message is not None
    assert "You have already voted for this race" == flash_message


# Mocked function format may need to change slightly once the real implementation is added
def test_candidate_show_page(session, test_client, login, mocker):
    mocked_get_candidate = mocker.patch(
        "project.user_profiles.user_profiles.get_candidate",
        return_value={
            "image": "https://cdn.vox-cdn.com/thumbor/rhZpM6DYZlh10boukPzM_ZBbv5w=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/19608331/1193798833.jpg.jpg",
            "name": "Joe Biden",
            "age": 79,
            "description": "Joseph Robinette Biden Jr. is an American politician who is the 46th and current president of the United States. A member of the Democratic Party, he served as the 47th vice president from 2009 to 2017 under Barack Obama and represented Delaware in the United States Senate from 1973 to 2009.",
            "race": {"title": "Presidential", "id": 1},
        },
    )

    response = test_client.get("/candidate/1")
    print(response.data)

    mocked_get_candidate.assert_called_with(1)
    assert str.encode("Joe Biden") in response.data
    assert str.encode("Presidential") in response.data


def test_abstain(session, test_client, login, mocker):
    mocked_has_voted = mocker.patch(
        "project.user_profiles.user_profiles.has_voted", return_value=False
    )
    mocked_get_race = mocker.patch(
        "project.user_profiles.user_profiles.get_race",
        return_value={"Name": "President", "Date": "04/22/2022", "id": 1},
    )

    response = test_client.post("/abstain/1")

    mocked_has_voted.assert_called_with(1, 1)
    mocked_get_race.assert_called_with(1)

    with test_client.session_transaction() as session:
        flash_message = dict(session["_flashes"]).get("info")

    # Assert
    assert response.status_code == 302
    assert flash_message is not None
    assert "You have abstained from the following race: President" == flash_message


def test_duplicate_abstain(session, test_client, login, mocker):
    mocked_has_voted = mocker.patch(
        "project.user_profiles.user_profiles.has_voted", return_value=True
    )

    response = test_client.post("/abstain/1")

    mocked_has_voted.assert_called_with(1, 1)

    with test_client.session_transaction() as session:
        flash_message = dict(session["_flashes"]).get("info")

    # Assert
    assert response.status_code == 302
    assert flash_message is not None
    assert "You have already voted for this race" == flash_message


def test_vote(session, test_client, login, mocker):
    mocked_has_voted = mocker.patch(
        "project.user_profiles.user_profiles.has_voted", return_value=False
    )
    mocked_get_candidate = mocker.patch(
        "project.user_profiles.user_profiles.get_candidate",
        return_value={
            "image": "https://cdn.vox-cdn.com/thumbor/rhZpM6DYZlh10boukPzM_ZBbv5w=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/19608331/1193798833.jpg.jpg",
            "name": "Joe Biden",
            "age": 79,
            "description": "Joseph Robinette Biden Jr. is an American politician who is the 46th and current president of the United States. A member of the Democratic Party, he served as the 47th vice president from 2009 to 2017 under Barack Obama and represented Delaware in the United States Senate from 1973 to 2009.",
            "race": {"title": "Presidential", "id": 1},
        },
    )
    mocked_get_race = mocker.patch(
        "project.user_profiles.user_profiles.get_race",
        return_value={"Name": "President", "Date": "04/22/2022", "id": 1},
    )

    response = test_client.post("/vote/1", data={"candidate_id": 1, "pin": 123456})

    mocked_get_candidate.assert_called_with("1")
    mocked_has_voted.assert_called_with(1, 1)
    mocked_get_race.assert_called_with(1)

    with test_client.session_transaction() as session:
        flash_message = dict(session["_flashes"]).get("info")

    # Assert
    assert response.status_code == 302
    assert flash_message is not None
    assert "Vote successfully submitted for President Joe Biden" == flash_message


def test_duplicate_vote(session, test_client, login, mocker):
    mocked_has_voted = mocker.patch(
        "project.user_profiles.user_profiles.has_voted", return_value=True
    )

    response = test_client.post("/vote/1",  data={"candidate_id": 1, "pin": 123456})

    mocked_has_voted.assert_called_with(1, 1)

    with test_client.session_transaction() as session:
        flash_message = dict(session["_flashes"]).get("info")

    # Assert
    assert response.status_code == 302
    assert flash_message is not None
    assert "You have already voted for this race" == flash_message


def test_voter_summary(session, test_client, login, mocker, vote):
    mocked_get_user_votes_for_election = mocker.patch(
        "project.user_profiles.user_profiles.get_user_votes_for_election", return_value=[{"race_id": 17867, "candidate_id": 276, "created": "DATE_CREATED"}]
    )

    mocked_get_election = mocker.patch(
        "project.user_profiles.user_profiles.get_election", return_value={"id": 1}
    )

    response = test_client.get("/summary/1?pin_input=123456")

    mocked_get_user_votes_for_election.assert_called_with(1, '123456')
    mocked_get_election.assert_called_with(1)

    # Assert
    assert response.status_code == 200
    assert str.encode("276") in response.data
    assert str.encode("17867") in response.data
    assert str.encode("DATE_CREATED") in response.data


def test_get_user_votes_for_election(session, test_client, login, mocker, vote):
    pin = vote
    mocked_get_election_races = mocker.patch(
        "project.user_profiles.user_profiles.get_election_races",
        return_value=[{"Name": "President", "Date": "04/22/2022", "id": 1}]
    )

    votes = get_user_votes_for_election(1, pin)

    mocked_get_election_races.assert_called_with(election_id=1)

    # Assertions will need updated when real databases are integrated
    assert len(votes) == 1
    assert votes[0].race_id == 1
    assert votes[0].candidate_id == 1
    assert votes[0].pin == str(pin)


def test_has_voted_not_yet_voted(session, test_client, login, mocker):
    assert not has_voted(1, 1)


def test_has_voted_after_vote(session, test_client, login, mocker):
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

    test_client.post("/vote/1", data={"candidate_id": 1, "pin": 123456})
    assert has_voted(1, 1)
