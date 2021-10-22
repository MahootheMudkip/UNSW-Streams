import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "message/senddm/v1"

@pytest.fixture
def initial_setup():
    # clear all stored data
    requests.delete(url + "clear/v1")

    # url routes
    auth_register_url = url + "auth/register/v2"
    dm_create_url = url + "dm/create/v1"

    # create new user 0, (global owner) and extracts token
    user0_response = requests.post(auth_register_url, json={      
        "email":        "theboss@gmail.com", 
        "password":     "999999",
        "name_first":   "Big", 
        "name_last":    "Boss"
    })
    user0 = user0_response.json()
    user0_token = user0["token"]

    # create new user 1 and extract token
    user1_response = requests.post(auth_register_url, json={      
        "email":        "lmao@gmail.com", 
        "password":     "123789",
        "name_first":   "Jeremy", 
        "name_last":    "Clarkson"
    })
    user1 = user1_response.json()
    user1_token = user1["token"]

    # create dm and extract dm_id
    dm_response = requests.post(dm_create_url, json={
        "token":        user0_token,
        "u_ids":        []
    })
    dm_id = dm_response.json()["dm_id"]

    return {
        "user0_token":  user0_token,
        "user1_token":  user1_token,
        "dm_id":        dm_id
    }

# testing valid token, invalid dm_id
def test_message_senddm_invalid_dm_id(initial_setup):
    user0_token = initial_setup["user0_token"]
    response = requests.post(URL, json={
        "token":        user0_token,
        "dm_id":        -34587678,
        "message":      "hello world"
    })
    assert response.status_code == INPUT_ERROR

# testing invalid token, valid dm_id
def test_message_senddm_invalid_token(initial_setup):
    dm_id = initial_setup["dm_id"]
    response = requests.post(URL, json={
        "token":        "kjkjd",
        "dm_id":        dm_id,
        "message":      "hello world"
    })
    assert response.status_code == ACCESS_ERROR

# testing normal user (not a member) trying to access valid dm
def test_message_senddm_unauthorised_user(initial_setup):
    user1_token = initial_setup["user1_token"]
    dm_id = initial_setup["dm_id"]

    response1 = requests.post(URL, json={
        "token":        user1_token,
        "dm_id":        dm_id,
        "message":      "hello world"
    })
    assert response1.status_code == ACCESS_ERROR

# token and dm_id both invalid
def test_message_senddm_invalid_token_and_dm_id(initial_setup):
    response = requests.post(URL, json={
        "token":        "4534",
        "dm_id":        -45857,
        "message":      "hello world"
    })
    assert response.status_code == ACCESS_ERROR

# valid user, invalid dm_id, invalid message
def test_message_senddm_invalid_dm_id_and_message(initial_setup):
    user0_token = initial_setup["user0_token"]

    response1 = requests.post(URL, json={
        "token":        user0_token,
        "dm_id":        -3423,
        "message":      ""
    })
    assert response1.status_code == INPUT_ERROR

# user not in dm, message invalid
def test_message_senddm_not_member_invalid_message(initial_setup):
    user1_token = initial_setup["user1_token"]
    dm_id = initial_setup["dm_id"]

    response1 = requests.post(URL, json={
        "token":        user1_token,
        "dm_id":        dm_id,
        "message":      ""
    })
    assert response1.status_code == ACCESS_ERROR

# valid user and dm_id, invalid message
def test_message_senddm_invalid_message(initial_setup):
    user0_token = initial_setup["user0_token"]
    dm_id = initial_setup["dm_id"]

    response1 = requests.post(URL, json={
        "token":        user0_token,
        "dm_id":        dm_id,
        "message":      ""
    })
    assert response1.status_code == INPUT_ERROR
