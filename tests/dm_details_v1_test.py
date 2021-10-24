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
        "email": "user1@gmail.com",
        "password": "password",
        "name_first": "Luke",
        "name_last": "Pierce"

    })
    token1 = response1.json()["token"]

    # create user 2
    response2 = requests.post(url + "auth/register/v2", json={
        "email": "user2@gmail.com",
        "password": "password",
        "name_first": "Artem",
        "name_last": "Wing"

    })
    token2 = response2.json()["token"]

    # create user 3
    response3 = requests.post(url + "auth/register/v2", json={
        "email": "user3@gmail.com",
        "password": "password",
        "name_first": "Vyn",
        "name_last": "Ritcher"

    })
    token3 = response3.json()["token"]

    # create user 4 
    response4 = requests.post(url + "auth/register/v2", json={
        "email": "user4@gmail.com",
        "password": "password",
        "name_first": "Marius",
        "name_last": "Von hagen"

    })
    token4 = response4.json()["token"]

    response = requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1, 2]
    })
    dm_id = response.json()["dm_id"]
    values = {
        "token1": token1,
        "token2": token2,
        "token3": token3,
        "token4": token4,
        "dm_id": dm_id
    }

    return values

# token given is invalid
def test_dm_details_invalid_token(data):
    response = requests.get(url + "dm/details/v1", params={
        "token" : "wrong token",
        "dm_id": data["dm_id"]
    })
    assert response.status_code == ACCESS_ERROR

# dm_id given doesn't exist
def test_dm_details_dm_id_doesnt_exist_token(data):
    response = requests.get(url + "dm/details/v1", params={
        "token" : data["token1"],
        "dm_id": -1
    })
    assert response.status_code == INPUT_ERROR

# user requesting details is not in dm
def test_dm_details_user_not_in_dm(data):
    response = requests.get(url + "dm/details/v1", params={
        "token" : data["token4"],
        "dm_id": data["dm_id"]
    })
    assert response.status_code == ACCESS_ERROR

# correct details should be displayed if valid id and dm_id
def test_dm_details_correct_details(data):
    response = requests.get(url + "dm/details/v1", params={
        "token": data["token1"],
        "dm_id": data["dm_id"]
    })
    assert response.status_code ==  NO_ERROR

    dm_name = response.json()["name"]
    dm_members = response.json()["members"]

    # checking if dm name is correct
    assert dm_name == "artemwing, lukepierce, vynritcher"
    
    # checking if dm_members are correct
    assert len(dm_members) == 3

    # checking individual fields of users are correct
    assert dm_members[0]["u_id"] == 1
    assert dm_members[0]["email"] == "user2@gmail.com"
    assert dm_members[0]["name_first"] == "Artem"
    assert dm_members[0]["name_last"] == "Wing"
    assert dm_members[0]["handle_str"] == "artemwing"

    # checking individual fields of users are correct
    assert dm_members[1]["u_id"] == 2
    assert dm_members[1]["email"] == "user3@gmail.com"
    assert dm_members[1]["name_first"] == "Vyn"
    assert dm_members[1]["name_last"] == "Ritcher"
    assert dm_members[1]["handle_str"] == "vynritcher"

    # checking individual fields of users are correct
    assert dm_members[2]["u_id"] == 0
    assert dm_members[2]["email"] == "user1@gmail.com"
    assert dm_members[2]["name_first"] == "Luke"
    assert dm_members[2]["name_last"] == "Pierce"
    assert dm_members[2]["handle_str"] == "lukepierce"

