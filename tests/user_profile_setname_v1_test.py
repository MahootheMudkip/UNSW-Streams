import json
from src.error import InputError
import pytest
import requests
from src.config import url

INPUT_ERROR = 400
NO_ERROR = 200

URL = url + "user/profile/setname/v1"

@pytest.fixture
def setup():
    requests.delete(url + "clear/v1")

    user1_info = {
        "email" : "email1@gmail.com", 
        "password" : "password1",
        "name_first" : "John",
        "name_last" : "Smith" 
    }

    response1 = requests.post(url + "auth/register/v2", json=user1_info)
    tok = response1.json()["token"]
    u_id = response1.json()["auth_user_id"]

    return {
        "tok": tok,
        "u_id": u_id
    }

# Input names are less than 1 character
def test_user_profile_setname_v1_too_short(setup):
    token = setup["tok"]
    # first name too short, last name ok
    response = requests.put(URL, json={"token":token,"name_first":"", "name_last":"Shepherd"})
    assert response.status_code == INPUT_ERROR
    # last name too short, first name ok
    response = requests.put(URL, json={"token":token,"name_first":"Karen", "name_last":""})
    assert response.status_code == INPUT_ERROR
    # first name too short, last name too short
    response = requests.put(URL, json={"token":token,"name_first":"", "name_last":""})
    assert response.status_code == INPUT_ERROR

# Input names are more than 51 characters
def test_user_profile_setname_v1_too_long(setup):
    token = setup["tok"]
    # first name too long, last name ok
    response = requests.put(URL, json={
        "token":token,
        "name_first":"NMuxCSwfagbkYzMk7m3c1qV937zFNdzTNykOJP3MZlv0Au7tgPP",
        "name_last":"Shepherd"
    })
    assert response.status_code == INPUT_ERROR
    # last name too long, first name ok
    response = requests.put(URL, json={
        "token":token,
        "name_first":"Karen", 
        "name_last":"NMuxCSwfagbkYzMk7m3c1qV937zFNdzTNykOJP3MZlv0Au7tgPP"
    })
    assert response.status_code == INPUT_ERROR
    # first name too long, last name too long
    response = requests.put(URL, json={"token":token,
        "name_first":"NMuxCSwfagbkYzMk7m3c1qV937zFNdzTNykOJP3MZlv0Au7tgPP",
        "name_last":"NMuxCSwfagbkYzMk7m3c1qV937zFNdzTNykOJP3MZlv0Au7tgPP"
    })
    assert response.status_code == INPUT_ERROR

# Input name is same as original
def test_user_profile_setname_v1_same_name(setup):
    token = setup["tok"]
    u_id = setup["u_id"]

    response = requests.put(URL, json={"token":token,"name_first":"John", "name_last":"Smith"})
    assert response.status_code == NO_ERROR

    response = requests.get(url + "user/profile/v1", params={"token":token,"u_id":u_id})
    assert response.json()["user"]["name_first"] == "John"
    assert response.json()["user"]["name_last"] == "Smith"

# Input names are different from original
def test_user_profile_setname_v1_different_name(setup):
    token = setup["tok"]
    u_id = setup["u_id"]

    response = requests.put(URL, json={"token":token,"name_first":"Bob", "name_last":"Dylan"})
    assert response.status_code == NO_ERROR

    response = requests.get(url + "user/profile/v1", params={"token":token,"u_id":u_id})
    assert response.json()["user"]["name_first"] == "Bob"
    assert response.json()["user"]["name_last"] == "Dylan"


