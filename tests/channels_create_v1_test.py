import pytest 
import requests
from src.config import url
from json import loads

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

@pytest.fixture
def data(): 
    requests.delete(url + "clear/v1")
    #create a User
    user1_info = {
        "email": "dead@inside.com",
        "password": "5343q46",
        "name_first": "Pablo",
        "name_last": "Escobar"
    }
    user2_info = {
        "email": "Ineed@sleep.com",
        "password": "4zxcv43",
        "name_first": "sponge",
        "name_last": "bob"
    }
    user1 = requests.post(url + "auth/register/v2", json=user1_info )
    token1 = user1.json()["token"]

    user2 = requests.post(url + "auth/register/v2", json=user2_info )
    token2 = user2.json()["token"]

    values = {
        "token1" : token1,
        "token2" : token2
    }
    return values

#testing when the user is invalid and a valid name
def test_channels_create_v1_invalid_token(data):
    # token in wrong format
    response1 = requests.post(url + "channels/create/v2", json={"token":"invalid.token", "name":"Mr. Krabs", "is_public":True})
    assert response1.status_code == ACCESS_ERROR

    # session that token refers to does not exist
    response2 = requests.post(url + "channels/create/v2", json={"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjAsInNlc3Npb25faWQiOjJ9.5z6iOer-E9r8C_gxBLusZJlUi5cVbl6YAyZFT8-a42o", "name":"Channel1", "is_public":False})
    assert response2.status_code == ACCESS_ERROR

#testing when the user is invalid and invalid name 
def test_channels_create_v1_both_invalid(data):
    #less than one character
    response1 = requests.post(url + "channels/create/v2", json={"token":"invalid.token", "name":"", "is_public":True})
    assert response1.status_code == ACCESS_ERROR
    #greater than 20 character
    response2 = requests.post(url + "channels/create/v2", json={"token":"invalid.token", "name":"abcdefghijklmnopqrstuvwxyz", "is_public":True})
    assert response2.status_code == ACCESS_ERROR

#testing when the user is valid with a invalid name 
def test_channels_create_v1_invalid_name(data):
    token1 = data["token1"]
    token2 = data["token2"]

    #less than one character
    response1 = requests.post(url + "channels/create/v2", json={"token":token1, "name":"", "is_public":True})
    assert response1.status_code == INPUT_ERROR
    #greater than 20 character
    response2 = requests.post(url + "channels/create/v2", json={"token":token2, "name":"abcdefghijklmnopqrstuvwxyz", "is_public":False})
    assert response2.status_code == INPUT_ERROR

#testing when the user is valid with a valid name 
def test_channels_create_v1_valid_parameters(data):
    token1 = data["token1"]
    token2 = data["token2"]

    response = requests.post(url + "channels/create/v2", json={"token":token1, "name":"Channel1", "is_public":True})
    assert response.status_code == NO_ERROR
    channel1_id = response.json()["channel_id"]

    response = requests.get(url + "channel/details/v2", params={"token":token1, "channel_id":channel1_id})
    assert response.status_code == NO_ERROR
    channel_info1 = response.json() 

    assert (channel_info1["name"] == "Channel1")
    assert (channel_info1["is_public"] == True)
    assert (len(channel_info1["owner_members"]) == 1)
    assert (len(channel_info1["all_members"]) == 1)

    response = requests.post(url + "channels/create/v2", json={"token":token2, "name":"Channel2", "is_public":False})
    assert response.status_code == NO_ERROR
    channel2_id = response.json()["channel_id"]

    response = requests.get(url + "channel/details/v2", params={"token":token2, "channel_id":channel2_id})
    assert response.status_code == NO_ERROR
    channel_info2 = response.json()

    assert (channel_info2["name"] == "Channel2")
    assert (channel_info2["is_public"] == False)
    assert (len(channel_info2["owner_members"]) == 1)
    assert (len(channel_info2["all_members"]) == 1)
