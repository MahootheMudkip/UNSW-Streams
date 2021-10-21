import json
import pytest
import requests
from src.config import url
from src.data_store import data_store

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

@pytest.fixture
def data():
    #clear 
    requests.delete(url + 'clear/v1')

    #create a user
    user1_res = requests.post(url + "auth/register/v2", 
    json = {      
        "email":        "will@mill.com", 
        "password":     "wea8732r4d",
        "name_first":   "bill", 
        "name_last":    "jill"
    })
    user1 = user1_res.json()
    user1_token = user1["token"]
    user1_id = user1["auth_user_id"]

    #create a user
    user2_res = requests.post(url + "auth/register/v2", 
    json = {      
        "email":        "never@gonna.com", 
        "password":     "4weFU21S",
        "name_first":   "give", 
        "name_last":    "you_up"
    })
    user2 = user2_res.json()
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]

    #create a user
    user3_res = requests.post(url + "auth/register/v2", 
    json = {      
        "email":        "never@gona.com", 
        "password":     "r23rhbjk",
        "name_first":   "let", 
        "name_last":    "you_down"
    })
    user3 = user3_res.json()
    user3_token = user3["token"]
    user3_id = user3["auth_user_id"]

    return {
        "user1_token" : user1_token,
        "user2_token" : user2_token,
        "user3_token" : user3_token,
        "user1_id"    : user1_id,
        "user2_id"    : user2_id,
        "user3_id"    : user3_id
    }

# test list of u_ids given is invalid
def test_invalid_u_id(data):
    token = data["user1_token"]
    u_ids = [-32,235,65]
    response = requests.post(url + "dm/create/v1", 
    json = {
        "token":    token,
        "u_ids":    u_ids  
    })
    assert response.status_code == INPUT_ERROR

# token given is invalid
def test_invalid_token(data):
    u_ids = [data["user2_token"], data["user3_token"]]
    response = requests.post(url + "dm/create/v1", 
    json = {
        "token":    "yoyoyo",
        "u_ids":    u_ids  
    })
    assert response.status_code == ACCESS_ERROR

# token and u_id given are both invalid
def test_invalid_token_invalid_id(data):
    response = requests.post(url + "dm/create/v1", 
    json = {
        "token":    "yoyoyo",
        "u_ids":    [-25]  
    })
    assert response.status_code == ACCESS_ERROR

# valid token and list of u_ids
def test_valid_dm_creation(data):
    dm_ids = []
    u_ids = [data["user2_id"], data["user3_id"]]
    i = 0
    while i < 50:
        response = requests.post(url + "dm/create/v1", 
        json = {
            "token":    data["user1_token"],
            "u_ids":    u_ids  
        })
        assert response.status_code == NO_ERROR
        dm_ids.append(response.json()["dm_id"])
        i += 1
        
    assert len(set(dm_ids)) == 50

def test_dm_create_correct_dm_id(data):
    u_ids = [data["user2_id"], data["user3_id"]]
    response = requests.post(url + "dm/create/v1", json={"token":data["user1_token"],"u_ids":u_ids})
    assert response.status_code == NO_ERROR
    assert response.json()["dm_id"] == 0

    response = requests.post(url + "dm/create/v1", json={"token":data["user1_token"],"u_ids":u_ids})
    assert response.status_code == NO_ERROR
    assert response.json()["dm_id"] == 1

    response = requests.post(url + "dm/create/v1", json={"token":data["user1_token"],"u_ids":u_ids})
    assert response.status_code == NO_ERROR
    assert response.json()["dm_id"] == 2

    response = requests.post(url + "dm/create/v1", json={"token":data["user1_token"],"u_ids":u_ids})
    assert response.status_code == NO_ERROR
    assert response.json()["dm_id"] == 3
    