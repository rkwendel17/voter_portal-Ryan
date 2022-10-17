def create_precinct(
    test_client,
    name="precinct_name",
    phone_number="123-456-7890",
    manager_id=1,
    zip_ranges=None,
    ship_address="123 street address",
    address2="apt3",
    locality="Iowa City",
    state="Iowa",
    postcode="52240",
    country="USA",
):
    if zip_ranges is None:
        zip_ranges = {"zip-start-1": "22222-3000", "zip-end-1": "22222-8000"}

    data = {
        "precinct_name": name,
        "phone_number": phone_number,
        "poll_manager": manager_id,
        "ship-address": ship_address,
        "address2": address2,
        "locality": locality,
        "state": state,
        "postcode": postcode,
        "country": country,
    }

    data.update(zip_ranges)

    response = test_client.post("/precinct/new", data=data, follow_redirects=True)
    return response


def test_precinct_invaid_address_validation(session, test_client, login):
    """Variant 1: Go to precinct creation page. Fill out the form properly,
    but enter an invalid address. Observe that an error message is
    displayed and that the submit button does not proceed to
    the next screen."""
    response = create_precinct(test_client, state="notastate")
    assert (
        b"The following issues were found when validating your address:\n\tField &#39;State&#39; is invalid\n"
        in response.data
    )
    assert (
        b"Precinct Creation Page" in response.data
    )  # to ensure we remained on the same page


def test_precinct_invaid_phone_number_validation(session, test_client, login):
    """Variant 1: Go to precinct creation page. Fill out the form properly,
    but enter an imporperly formatted phone number. Observe that an error
    message is displayed and that the submit button does not proceed to
    the next screen."""
    response = create_precinct(test_client, phone_number="notanumber")
    print(response.data)
    assert (
        b"Invalid phone number format, please follow the form xxx-xxx-xxxx."
        in response.data
    )
    assert (
        b"Precinct Creation Page" in response.data
    )  # to ensure we remained on the same page


def test_precinct_invaid_manager_validation(session, test_client, login):
    """Send a post request to the precenct creation page with an
    invalid manager ID, verify tht an error is returned."""
    response = create_precinct(test_client, manager_id=1111)
    print(response.data)
    assert b"No manager exists with the given ID" in response.data
    assert (
        b"Precinct Creation Page" in response.data
    )  # to ensure we remained on the same page


def test_precinct_invaid_zipcode_range_validation(session, test_client, login):
    """Send a post request to the precinct creation page with
    an invalid zipcode range, verify tht an error is returned."""
    response = create_precinct(
        test_client, zip_ranges={"zip-start-1": "22222-3000", "zip-end-1": "22222-1000"}
    )
    print(response.data)
    assert (
        b"A zipcode range cannot have a end value of 222221000 that is less than it&#39;s start value of 222223000"
        in response.data
    )
    assert (
        b"Precinct Creation Page" in response.data
    )  # to ensure we remained on the same page


def test_precinct_missing_zipcode_range_validation(session, test_client, login):
    """Send a post request to the precenct creation page without any
    zipcode ranges. Expect to receive error message."""
    response = create_precinct(test_client, zip_ranges={})
    print(response.data)
    assert b"Please enter at least one zipcode range" in response.data
    assert (
        b"Precinct Creation Page" in response.data
    )  # to ensure we remained on the same page


def test_valid_precinct(session, test_client, login):
    """Send a post request to the precenct creation page without any
    zipcode ranges. Expect to receive error message."""
    response = create_precinct(test_client, name="valid_precinct")
    print(response.data)
    assert response.status_code == 200
    assert (
        str.encode(f"Precinct valid_precinct was successfully created") in response.data
    )
