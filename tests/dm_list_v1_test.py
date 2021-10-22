import pytest
import requests
from src.config import url
import json

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200


@pytest.fixture
def data():
    #clear
    requests.delete(url + "clear/v1")

    #create user 1
    user1_response = requests.post(url + "auth/register/v2", 
    json = {      
        "email":        "jwa@yamw.com", 
        "password":     "rb4t43gd",
        "name_first":   "don", 
        "name_last":    "jqfe"
    })
    user1 = json.loads(user1_response.text)
    user1_token = user1["token"]
    user1_id = user1["auth_user_id"]

    #create user 2
    user2_response = requests.post(url + "auth/register/v2", 
    json = {      
        "email":        "cat@mat.com", 
        "password":     "r3wavaa",
        "name_first":   "rat", 
        "name_last":    "sat"
    })
    user2 = json.loads(user2_response.text)
    user2_token = user2["token"]
    

    #create user 3
    user3_response = requests.post(url + "auth/register/v2", 
    json = {      
        "email":        "abc@def.com", 
        "password":     "kjb4433",
        "name_first":   "ghi", 
        "name_last":    "jkl"
    })
    user3 = json.loads(user3_response.text)
    user3_token = user3["token"]
    user3_id = user3["auth_user_id"]
    
    #create a dm with only one user
    dm_create1_res = requests.post (url + "dm/create/v1", 
    json = {
        "token" : user1_token,
        "u_ids" : []
    })
    dm1 = dm_create1_res.json()
    dm1_id = dm1["dm_id"]

    #create a dm with all 3 members
    dm_create2_res = requests.post (url + "dm/create/v1", 
    json = {
        "token" : user2_token,
        "u_ids" : [user1_id, user3_id]
    })
    dm2 = dm_create2_res.json()
    dm2_id = dm2["dm_id"]

    #create a dm with 2 members
    dm_create3_res = requests.post (url + "dm/create/v1", 
    json = {
        "token" : user2_token,
        "u_ids" : [user3_id]
    })
    dm3 = dm_create3_res.json()
    dm3_id = dm3["dm_id"]

    return {
        "user1_token" : user1_token,
        "user2_token" : user2_token,
        "user3_token" : user3_token,
        "dm1_id" : dm1_id,
        "dm2_id" : dm2_id,
        "dm3_id" : dm3_id
    }
    

def test_invalid_token(data):
    response = requests.get(url + "dm/list/v1", params={
        "token":    "yoyoyo",
    })
    assert response.status_code == ACCESS_ERROR

#test number users returned in a dm
def test_num_dm(data):
    token1 = data["user1_token"]
    token2 = data["user2_token"]

    #check for user 1
    response1 = requests.get(url + "dm/list/v1", params={
        "token":    token1
    })
    assert response1.status_code == NO_ERROR
    data1 = response1.json()
    assert (len(data1["dms"]) == 2)

    #check for user 2
    response2 = requests.get(url + "dm/list/v1", params={
        "token":    token2,
    })
    assert response2.status_code == NO_ERROR
    data2 = response2.json()
    assert (len(data2["dms"]) == 2)


#test deatils of dms list returned
def test_returned_details(data):
    token1 = data["user1_token"]
    token2 = data["user2_token"]
    token3 = data["user3_token"]
    dm1_id = data["dm1_id"]
    dm2_id = data["dm2_id"]
    dm3_id = data["dm3_id"]

    #check dm id for user 1
    dm_id_response1 = requests.get(url + "dm/list/v1", 
    params = {
        "token": token1
    })
    assert dm_id_response1.status_code == NO_ERROR
    data1 = dm_id_response1.json()
    assert (data1["dms"][0]["dm_id"] == dm1_id)
    assert (data1["dms"][0]["name"] == "donjqfe")    

    #check dm id for user 2
    dm_id_response2 = requests.get(url + "dm/list/v1", 
    params = {
        "token":    token2
    })
    assert dm_id_response2.status_code == NO_ERROR
    data2 = dm_id_response2.json()
    assert (data2["dms"][0]["dm_id"] == dm2_id)
    assert (data2["dms"][1]["dm_id"] == dm3_id)
    assert (data2["dms"][0]["name"] == "donjqfe, ghijkl, ratsat")
    assert (data2["dms"][1]["name"] == "ghijkl, ratsat") 

    #check dm id for user 3
    dm_id_response3 = requests.get(url + "dm/list/v1", 
    params = {
        "token":    token3
    })
    assert dm_id_response3.status_code == NO_ERROR
    data3 = dm_id_response3.json()
    assert (data3["dms"][1]["name"] == "ghijkl, ratsat")
    assert (data3["dms"][0]["dm_id"] == dm2_id)
    assert (data3["dms"][1]["dm_id"] == dm3_id)
    
    

