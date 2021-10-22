import json
from src.error import InputError
import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

URL = url + "user/profile/setemail/v1"

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
    assert(response1.status_code == NO_ERROR)
    tok1 = response1.json()["token"]
    u_id1 = response1.json()["auth_user_id"]

    user2_info = {
        "email" : "taken@email.com", 
        "password" : "password1",
        "name_first" : "John",
        "name_last" : "Smith" 
    }

    response2 = requests.post(url + "auth/register/v2", json=user2_info)
    assert(response2.status_code == NO_ERROR)

    return {
        "tok1": tok1,
        "u_id1": u_id1
    }

# test invalid token
def test_invalid_token():
    response = requests.put(URL, json={"token":1557, "email": "invalid_email.com"})
    assert response.status_code == ACCESS_ERROR    

# email does not match regex 
def test_register_email_invalid(setup):
    token = setup["tok1"]
    response = requests.put(URL, json={"token":token, "email": "invalid_email.com"})
    assert response.status_code == INPUT_ERROR

# email has already been registered
def test_register_email_taken(setup):
    token = setup["tok1"]
    response = requests.put(URL, json={"token":token, "email": "taken@email.com"})
    assert response.status_code == INPUT_ERROR

# test update email
def test_valid_email(setup):
    token = setup["tok1"]
    u_id = setup["u_id1"]
    response = requests.put(URL, json={"token":token, "email": "valid@email.com"})
    assert response.status_code == NO_ERROR

    response = requests.get(url + "user/profile/v1", params={"token":token,"u_id":u_id})
    assert response.json()["user"]["email"] == "valid@email.com"
