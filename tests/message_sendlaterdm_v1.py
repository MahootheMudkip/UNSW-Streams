import pytest
import requests
import json
from src.config import url
from datetime import *
import time

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

@pytest.fixture
def data():
    # clear 
    requests.delete(url + 'clear/v1')

    # create a user 
    response1 = requests.post(url + "auth/register/v2", 
    json={
        "email": "Pink@Floyd.com",
        "password": "qtu4h35",
        "name_first": "Floyd",
        "name_last": "Pink"

    })
    token1 = response1.json()["token"]
    user1_id = response1.json()["auth_user_id"]

    # create a user 
    response2 = requests.post(url + "auth/register/v2", 
    json={
        "email": "AC@DC.com",
        "password": "iuywqro3",
        "name_first": "AC",
        "name_last": "DC"
    })
    token2 = response2.json()["token"]
    user2_id = response1.json()["auth_user_id"]
    
    # create a user 
    response3 = requests.post(url + "auth/register/v2", 
    json={
        "email": "Brian@May.com",
        "password": "wreqro3",
        "name_first": "Brian",
        "name_last": "May"
    })
    token3 = response3.json()["token"]
    user3_id = response1.json()["auth_user_id"]

    #create a dm 1
    dm_response1 = requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [user2_id]
    })
    dm1_id = dm1_response.json()["dm_id"]

    #create a dm 2
    dm_response2 = requests.post(url + "dm/create/v1", json={
        "token": token2,
        "u_ids": [user1_id, user3_id]
    })
    dm2_id = dm2_response.json()["dm_id"]

    
    
    
    #get a unix timestamp of the current time
    timestamp = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())

    return {
        "token1" : token1,
        "token2" : token2,
        "token3" : token3,
        "dm1_id" : dm1_id,
        "dm2_id" : dm2_id ,
        "timestamp" : timestamp
    }

# testing valid token, invalid dm_id
def test_message_senddm_invalid_dm_id(initial_setup):
    
    response = requests.post(URL, json={
        "token":        data["token1"],
        "dm_id":        -4543,
        "message":      "jello"
    })
    assert response.status_code == INPUT_ERROR
