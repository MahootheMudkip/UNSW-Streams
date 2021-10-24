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
        "email": "kanye@east.com",
        "password": "32gfhbf",
        "name_first": "kanye",
        "name_last": "east"

    })
    token1 = response1.json()["token"]

    # create user 2
    response2 = requests.post(url + "auth/register/v2", json={
        "email": "el@chapo.com",
        "password": "dvfs8h9v4",
        "name_first": "el",
        "name_last": "chapo"

    })
    token2 = response2.json()["token"]

    # create user 3
    response3 = requests.post(url + "auth/register/v2", json={
        "email": "Hay@den.com",
        "password": "dvfs8h9v4",
        "name_first": "hay",
        "name_last": "den"

    })
    token3 = response3.json()["token"]

    #create dm 1
    response1 = requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1, 2]
    })
    dm_id1 = response1.json()["dm_id"]

    #create dm 2
    response2 = requests.post(url + "dm/create/v1", json={
        "token": token2,
        "u_ids": [0, 2]
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
    response = requests.delete(url + "dm/remove/v1", json={
        "token" : "abcde",
        "dm_id": data["dm_id1"]
    })
    assert response.status_code == ACCESS_ERROR

# dm_id given doesn't exist
def test_dm_details_dm_id_doesnt_exist_token(data):
    response = requests.delete(url + "dm/remove/v1", json={
        "token" : data["token2"],
        "dm_id" : -434
    })
    assert response.status_code == INPUT_ERROR

# check if the person removing the dm is the owner
def test_owner_check(data):
    response1   = requests.delete(url + "dm/remove/v1", json={
        "token" : data["token3"],
        "dm_id" : data["dm_id1"]
    })
    assert response1.status_code == ACCESS_ERROR

    response2 = requests.delete(url + "dm/remove/v1", json={
        "token" : data["token1"],
        "dm_id" : data["dm_id1"]
    })
    assert response2.status_code == NO_ERROR

#check if the dm has been removed
def test_check_dm_removed(data):
    
    #get a list of dms of user with token and test
    dm_id_response1 = requests.get(url + "dm/list/v1", 
    params = {
        "token": data["token1"]
    })
    assert dm_id_response1.status_code == NO_ERROR
    data1 = dm_id_response1.json()
    assert (len(data1["dms"]) == 2)

    #remove a dm from dm's list 
    response1 = requests.delete(url + "dm/remove/v1", json={
        "token" : data["token1"],
        "dm_id": data["dm_id1"]
    })
    assert response1.status_code == NO_ERROR

    #git a list of dms of the same user and compare
    dm_id_response2 = requests.get(url + "dm/list/v1", 
    params = {
        "token": data["token1"]
    })
    assert dm_id_response2.status_code == NO_ERROR
    data2 = dm_id_response2.json()

    assert (len(data2["dms"]) == 1)


        
