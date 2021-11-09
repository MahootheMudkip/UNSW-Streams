import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "user/profile/v1"

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
    user0_id = user0["auth_user_id"]

    # create new user 1 and extract token
    user1_response = requests.post(auth_register_url, json={      
        "email":        "lmao@gmail.com", 
        "password":     "123789",
        "name_first":   "Jeremy", 
        "name_last":    "Clarkson"
    })
    user1 = user1_response.json()
    user1_token = user1["token"]
    user1_id = user1["auth_user_id"]

    # create new user 2 and extract token
    user2_response = requests.post(auth_register_url, json={      
        "email":        "wtf@gmail.com", 
        "password":     "234789",
        "name_first":   "James",
        "name_last":    "May"
    })
    user2 = user2_response.json()
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]

    return {
        "user0_token":          user0_token,
        "user0_id":             user0_id,
        "user1_token":          user1_token,
        "user1_id":             user1_id,
        "user2_token":          user2_token,
        "user2_id":             user2_id
    }

# test invalid token and u_id
def test_user_profile_v1_invalid_token_and_u_id(initial_setup):
    response = requests.get(URL, params={
        "token":    "i'mafaketoken",
        "u_id":     -234
    })
    assert response.status_code == ACCESS_ERROR

# test invalid token only
def test_user_profile_v1_invalid_token(initial_setup):
    user1_id = initial_setup["user1_id"]
    response = requests.get(URL, params={
        "token":    "i'mafaketoken",
        "u_id":     user1_id
    })
    assert response.status_code == ACCESS_ERROR

# test invalid u_id only
def test_user_profile_v1_invalid_u_id(initial_setup):
    user2_token = initial_setup["user2_token"]
    response = requests.get(URL, params={
        "token":    user2_token,
        "u_id":     -43348
    })
    assert response.status_code == INPUT_ERROR

# test all details
def test_user_profile_v1_correct_details(initial_setup):
    user0_token = initial_setup["user0_token"]
    user1_token = initial_setup["user1_token"]
    user0_id = initial_setup["user0_id"]
    user2_id = initial_setup["user2_id"]
    user2_token = initial_setup["user2_token"]
    user1_id = initial_setup["user1_id"]

    response = requests.get(URL, params={
        "token":    user0_token,
        "u_id":     user0_id
    })
    assert response.status_code == NO_ERROR
    data = response.json()

    assert len(data["user"]) == 6

    response2 = requests.get(URL, params={
        "token":    user1_token,
        "u_id":     user2_id
    })
    assert response2.status_code == NO_ERROR
    data2 = response2.json()

    assert len(data2["user"]) == 6

    response3 = requests.get(URL, params={
        "token":    user2_token,
        "u_id":     user1_id
    })
    assert response3.status_code == NO_ERROR
    data3 = response3.json()

    assert len(data3["user"]) == 6