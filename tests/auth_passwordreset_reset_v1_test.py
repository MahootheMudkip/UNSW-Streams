import pytest
import requests
from src.config import url

NO_ERROR = 200
ACCESS_ERROR = 403
INPUT_ERROR = 400
# error status codes

URL = url + "auth/passwordreset/reset/v1"

# valid reset code linked to user 1
VALID_RESET_CODE = "89a037064bc263646de4aad57c5589e68dbf88ad01ddd785e78e78b56a130707"
RECEIVER_EMAIL = "streamsapp.helper@gmail.com"

@pytest.fixture
def initial_setup():
    # clear all stored data
    requests.delete(url + "clear/v1")

    # url route
    auth_register_url = url + "auth/register/v2"

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
        "email":        RECEIVER_EMAIL, 
        "password":     "123789",
        "name_first":   "Jeremy", 
        "name_last":    "Clarkson"
    })
    user1 = user1_response.json()
    user1_token = user1["token"]

    # create new user 2 and extract token
    user2_response = requests.post(auth_register_url, json={      
        "email":        "wtf@gmail.com", 
        "password":     "234789",
        "name_first":   "James",
        "name_last":    "May"
    })
    user2 = user2_response.json()
    user2_token = user2["token"]

    return {
        "user0_token":          user0_token,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
    }

# testing invalid reset code only
def test_invalid_reset_code(initial_setup):
    response = requests.post(URL, json={
        "reset_code":   "lmao_me_fake",
        "new_password": "hellothere"
    })
    assert response.status_code == INPUT_ERROR

    response = requests.post(URL, json={
        "reset_code":   "a" * 64,
        "new_password": "hellothere"
    })
    assert response.status_code == INPUT_ERROR

# testing invalid new_password only
def test_invalid_new_password(initial_setup):
    response = requests.post(URL, json={
        "reset_code":   VALID_RESET_CODE,
        "new_password": "sdf"
    })
    assert response.status_code == INPUT_ERROR

# testing invalid new_password and reset code
def test_invalid_all(initial_setup):
    response = requests.post(URL, json={
        "reset_code":   "a" * 64,
        "new_password": "sdf"
    })
    assert response.status_code == INPUT_ERROR

# testing password changed
def test_user_with_given_email(initial_setup):
    response = requests.post(URL, json={
        "reset_code":   VALID_RESET_CODE,
        "new_password": "chicken"
    })
    assert response.status_code == NO_ERROR

    # first test with original password; should fail
    response = requests.post(url + "auth/login/v2", json={
        "email":    "streamsapp.helper@gmail.com",
        "password": "123789"
    })
    assert response.status_code == INPUT_ERROR

    # test with new email; should pass
    response = requests.post(url + "auth/login/v2", json={
        "email":    RECEIVER_EMAIL,
        "password": "chicken"
    })
    assert response.status_code == NO_ERROR
