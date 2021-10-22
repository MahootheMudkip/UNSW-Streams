from src import dm
from tests.channel_details_v2_test import ACCESS_ERROR, INPUT_ERROR
import pytest
import requests
import json
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200


@pytest.fixture
def data():
    # clear used data
    requests.delete(url + 'clear/v1')

    # create user 1
    response1 = requests.post(url + "auth/register/v2", json={
        "email": "Big@mac.com",
        "password": "32gfhbf",
        "name_first": "big",
        "name_last": "mac"

    })
    token1 = response1.json()["token"]

    # create user 2
    response2 = requests.post(url + "auth/register/v2", json={
        "email": "elon@lavender.com",
        "password": "dvfs8h9v4",
        "name_first": "elon",
        "name_last": "lavender"

    })
    token2 = response2.json()["token"]

    # create user 3
    response3 = requests.post(url + "auth/register/v2", json={
        "email": "roses@red.com",
        "password": "dvfs8h9v4",
        "name_first": "violets",
        "name_last": "blue"

    })
    token3 = response3.json()["token"]

    #create dm 1
    response1 = requests.post(url + "dm/create/v1", json={
        "token": token3,
        "u_ids": [0, 1]
    })
    dm_id1 = response1.json()["dm_id"]

    #create dm 2
    response2 = requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1]
    })
    dm_id2 = response2.json()["dm_id"]

    return {
        "token1" : token1,
        "token2" : token2,
        "token3" : token3,
        "dm_id1" : dm_id1,
        "dm_id2" : dm_id2
    }

#check if token is invalid
def test_dm_details_invalid_token(data):
    response = requests.post(url + "dm/leave/v1", json={
        "token" : "abcde",
        "dm_id": data["dm_id1"]
    })
    assert response.status_code == ACCESS_ERROR

# dm_id given doesn't exist
def test_dm_details_dm_id_invalid(data):
    response = requests.post(url + "dm/leave/v1", json={
        "token" : data["token2"],
        "dm_id" : -5346
    })
    assert response.status_code == INPUT_ERROR

# user not a part of the dm
def test_dm_details_user_not_in_dm(data):
    response = requests.post(url + "dm/leave/v1", json={
        "token" : data["token3"],
        "dm_id": data["dm_id2"]
    })
    assert response.status_code == ACCESS_ERROR

#check if user has actually left
def test_user_left(data):
    
    #when the owner leaves
    response1 = requests.post(url + "dm/leave/v1", json={
        "token" : data["token1"],
        "dm_id": data["dm_id2"]
    })
    assert response1.status_code == NO_ERROR

    #get a list of dms of user with token and test
    dm_id_response1 = requests.get(url + "dm/details/v1", 
    params = {
        "token" : data["token2"],
        "dm_id" : data["dm_id2"]
    })
    assert dm_id_response1.status_code == NO_ERROR
    data1 = dm_id_response1.json()

    assert len(data1["members"]) == 1

