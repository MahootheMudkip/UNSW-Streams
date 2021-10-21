import json
from src.error import InputError
import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

URL = url + "user/profile/sethandle/v1"

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
    tok1 = response1.json()["token"]
    u_id1 = response1.json()["auth_user_id"]

    user2_info = {
        "email" : "valid@mail.com", 
        "password" : "password1",
        "name_first" : "John",
        "name_last" : "Smith" 
    }

    response2 = requests.post(url + "auth/register/v2", json=user2_info)
    tok2 = response2.json()["token"]

    return {
        "tok1": tok1,
        "u_id1": u_id1,
        "tok2": tok2
    }

def test_invalid_token():
    response = requests.put(URL, json={"token":1557, "handle_str": "juancaca1"})
    assert response.status_code == ACCESS_ERROR

# test length of handle_str is not between 3 and 20 characters inclusive
def test_handle_str_length(setup):
    token = setup["tok1"]
    # handle is too short
    response = requests.put(URL, json={"token":token, "handle_str": "ju"})
    assert(response.status_code == INPUT_ERROR)
    # handle is too long
    response = requests.put(URL, json={"token":token, "handle_str": "juancarlospuyovelarde"})
    assert(response.status_code == INPUT_ERROR)


# test handle_str  contains characters that are not alphanumeric
def test_handle_str_alphanumeric(setup):
    token = setup["tok1"]
    response1 = requests.put(URL, json={"token":token, "handle_str": "$$$$$$"})
    assert(response1.status_code == INPUT_ERROR)
    response2 = requests.put(URL, json={"token":token, "handle_str": "juanca!!*"})
    assert(response2.status_code == INPUT_ERROR)

# test handle is already used by another user
def test_handle_str_is_taken(setup):
    token1 = setup["tok1"]
    response1 = requests.put(URL, json={"token":token1, "handle_str": "juanca"})
    assert(response1.status_code == NO_ERROR)
    
    token2 = setup["tok2"]
    response2 = requests.put(URL, json={"token":token2, "handle_str": "juanca"})
    assert(response2.status_code == INPUT_ERROR)

# test given handle is valid
def test_valid_handle(setup):
    token = setup["tok1"]
    u_id = setup["u_id1"]
    response1 = requests.put(URL, json={"token":token, "handle_str": "valid1"})
    assert(response1.status_code == NO_ERROR)

    response = requests.get(url + "user/profile/v1", params={"token":token,"u_id":u_id})
    assert response.json()["user"]["handle_str"] == "valid1"
