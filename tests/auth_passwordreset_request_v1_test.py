import pytest
import requests
from src.config import url

NO_ERROR = 200
ACCESS_ERROR = 403
# error status codes
URL = url + "auth/passwordreset/request/v1"
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

# testing email given does not belong to any user
# email not sent
def test_no_user_with_given_email(initial_setup):
    response = requests.post(URL, json={
        "email":    "fool@balrog.com",
    })
    assert response.status_code == NO_ERROR

# testing email given does belong to a user
# email sent
def test_user_with_given_email(initial_setup):
    response = requests.post(URL, json={
        "email":    RECEIVER_EMAIL
    })
    assert response.status_code == NO_ERROR

# testing email given does belong to a user is logged out
def test_user_with_given_email_logged_out(initial_setup):
    user1_token = initial_setup["user1_token"]

    response = requests.get(url + "channels/listall/v2", params={
        "token":    user1_token
    })
    assert response.status_code == NO_ERROR

    response = requests.post(URL, json={
        "email":    RECEIVER_EMAIL
    })
    assert response.status_code == NO_ERROR

    response = requests.get(url + "channels/listall/v2", params={
        "token":    user1_token
    })
    assert response.status_code == ACCESS_ERROR
    # since the user should have been logged out

def test_invalid_email(initial_setup):
    response = requests.post(URL, json={
        "email":    "invalid email"
    })
    assert response.status_code == NO_ERROR