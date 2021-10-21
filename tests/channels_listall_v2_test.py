import pytest
import requests
import json
from src.config import url

ACCESS_ERROR = 403
NO_ERROR = 200

@pytest.fixture
def data(): 
    requests.delete(url+ "clear/v1")
    
    #create a User
    user1_data = requests.post(url + "auth/register/v2", json={
        "email": "dead@inside.com", 
        "password": "53vsfsfgg46", 
        "name_first": "Pablo", 
        "name_last": "Escobar"
    })
    user1 = user1_data.json()
    user1_token = user1["token"]

    #create a User
    user2_data = requests.post (url + "auth/register/v2", json={
        "email": "Ineed@sleep.com", 
        "password": "43fsdvsfr", 
        "name_first": "sponge", 
        "name_last": "bob"
    })
    user2 = user2_data.json()
    user2_token = user2["token"]

    # make 5 new channels
    channel1 = requests.post(url + 'channels/create/v2', json={
        "token": user1_token,
        "name": "channel1",
        "is_public": True
    })
    channel1_id = channel1.json()["channel_id"]

    channel2 = requests.post(url + 'channels/create/v2', json={
        "token": user2_token,
        "name": "channel2",
        "is_public": False
    })
    channel2_id = channel2.json()["channel_id"]

    channel3 = requests.post(url + 'channels/create/v2', json={
        "token": user1_token,
        "name": "channel3",
        "is_public": True
    })
    channel3_id = channel3.json()["channel_id"]

    channel4 = requests.post(url + 'channels/create/v2', json={
        "token": user2_token,
        "name": "channel4",
        "is_public": False
    })
    channel4_id = channel4.json()["channel_id"]

    channel5 = requests.post(url + 'channels/create/v2', 
    json = {
        "token": user1_token,
        "name": "channel5",
        "is_public": True
    })
    channel5_id = channel5.json()["channel_id"]

    values = {
        "user1_token": user1_token,
        "user2_token": user2_token,
        "channel1_id": channel1_id,
        "channel2_id": channel2_id,
        "channel3_id": channel3_id,
        "channel4_id": channel4_id,
        "channel5_id": channel5_id,
    }
    return values

# token given is invalid
def test_channels_listall_invalid_token():
    response = requests.get(url + "channels/listall/v2", params={"token": "hello"})
    assert response.status_code == ACCESS_ERROR
    
#testing correct number of channels has been returned
def test_channels_listall_correct_length(data):
    user_token = data["user2_token"]
    response = requests.get(url + "channels/listall/v2", params={"token":user_token})
    assert response.status_code == NO_ERROR

    assert len(response.json()["channels"]) == 5

#testing if the right channel details have been returned
def test_channels_listall_v1_channels_returned(data):
    user_token1 = data["user1_token"]
    response1 = requests.get (url + 'channels/listall/v2', params={"token": user_token1})
    assert response1.status_code == NO_ERROR

    assert response1.json()["channels"][0]["name"] == "channel1"
    assert response1.json()["channels"][0]["channel_id"] == data["channel1_id"]
    assert response1.json()["channels"][1]["name"] == "channel2"
    assert response1.json()["channels"][1]["channel_id"] == data["channel2_id"]
    assert response1.json()["channels"][2]["name"] == "channel3"
    assert response1.json()["channels"][2]["channel_id"] == data["channel3_id"]
    assert response1.json()["channels"][3]["name"] == "channel4"
    assert response1.json()["channels"][3]["channel_id"] == data["channel4_id"]
    assert response1.json()["channels"][4]["name"] == "channel5"
    assert response1.json()["channels"][4]["channel_id"] == data["channel5_id"]