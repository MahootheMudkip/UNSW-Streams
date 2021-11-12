from src import dm
import pytest
import requests
import json
from src.config import url
import re

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

@pytest.fixture
def data():
    # clear used data
    requests.delete(url + 'clear/v1')

    # create user 1
    response1 = requests.post(url + "auth/register/v2", 
    json={
        "email": "jennifer@aniston.com",
        "password": "cwqasfgd4",
        "name_first": "jennifer",
        "name_last": "aniston"
    })
    token1 = response1.json()["token"]
    
    # create user 2
    response2 = requests.post(url + "auth/register/v2", 
    json={
        "email": "jennifer@lopez.com",
        "password": "nmievun4",
        "name_first": "jennifer",
        "name_last": "lopez"
    })
    token2 = response2.json()["token"]
    user2_id = response2.json()["auth_user_id"]

    # create user 3
    response3 = requests.post(url + "auth/register/v2", 
    json={
        "email": "jennifer@lawrence.com",
        "password": "bsbggrsdr",
        "name_first": "jennifer",
        "name_last": "lawrence"
    })
    token3 = response3.json()["token"]
    user3_id = response3.json()["auth_user_id"]

    #create a dm
    response = requests.post(url + "dm/create/v1", 
    json={
        "token": token1,
        "u_ids": [user2_id]
    })
    dm_id = response.json()["dm_id"]

    #create a channel
    channel_response = requests.post(url + "channels/create/v2", 
    json={
        "token":        token2,
        "name":         "Jennifer garner",
        "is_public":    True
    })
    assert channel_response.status_code == NO_ERROR
    channel_id = channel_response.json()["channel_id"]

    #add a user to the channel
    add_user_channel_resp = requests.post(url + 'channel/invite/v2', 
    json={
        "token": token2, 
        "channel_id": channel_id, 
        "u_id": user3_id
    }) 
    assert add_user_channel_resp.status_code == NO_ERROR
    
    #send a message in the channel
    channel_msg_resp = requests.post(url + "message/send/v1", 
    json={
        "token": token3,
        "channel_id": channel_id,
        "message": "Send this message or you die"
    })
    assert channel_msg_resp.status_code == NO_ERROR
    channel_message_id = channel_msg_resp.json()["message_id"]

    #send a message in the dm
    dm_msg_resp = response = requests.post(url + "message/senddm/v1", 
    json={
        "token":        token2,
        "dm_id":        dm_id,
        "message":      "hello from the other side"
    })
    assert dm_msg_resp.status_code == NO_ERROR
    dm_message_id = dm_msg_resp.json()["message_id"]

    return {
        "token1": token1,
        "token2": token2,
        "token3": token3,
        "user2_id" : user2_id,
        "dm_id": dm_id,
        "channel_id" : channel_id,
        "channel_message_id" : channel_message_id,
        "dm_message_id" : dm_message_id
    }


# testing invalid token
def test_message_share_invalid_token(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        "kjkjd",
        "og_message_id" : data["dm_message_id"],
        "message" : "fuuuuuuu",
        "channel_id":   data["channel_id"],
        "dm_id" : -1
    })
    assert response.status_code == ACCESS_ERROR

# testing when neither dm_id nor channel id is -1
def test_message_share_valid_ids(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token2"],
        "og_message_id" : data["channel_message_id"],
        "message" : "hfwa bhbb",
        "channel_id":   data["channel_id"],
        "dm_id" : data["dm_id"]
    })
    assert response.status_code == INPUT_ERROR
    
# testing when both dm_id and channel id are -1
def test_message_share_negative_ids(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token1"],
        "og_message_id" : data["dm_message_id"],
        "message" : "",
        "channel_id":   -1,
        "dm_id" : -1
    })
    assert response.status_code == INPUT_ERROR

#testing when sharing a message to a channel, user is not part of
def test_message_share_invalid_channelid(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token1"],
        "og_message_id" : data["dm_message_id"],
        "message" : "",
        "channel_id":   data["channel_id"],
        "dm_id" : -1
    })
    assert response.status_code == ACCESS_ERROR

#testing when sharing a message to a dm, user is not part of
def test_message_share_invalid_dmid(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token": data["token3"],
        "og_message_id" : data["channel_message_id"],
        "message" : "hubba hubba",
        "channel_id":   -1,
        "dm_id" : data["dm_id"]
    })
    assert response.status_code == ACCESS_ERROR

#testing when both channel id and dm id are invalid
def test_message_share_invalid_ids(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token3"],
        "og_message_id" : data["channel_message_id"],
        "message" : "",
        "channel_id":   -3456,
        "dm_id" : -65437
    })
    assert response.status_code == INPUT_ERROR

#testing when message_id from a channel/dm, user is not part
def test_message_share_messageid_invalid(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token2"],
        "og_message_id" : 2453647,
        "message" : "fuuuuuuu",
        "channel_id":   data["channel_id"],
        "dm_id" : -1
    })
    assert response.status_code == INPUT_ERROR

#testing when the length of the message is more than 1000 characters
def test_message_share_invalid_msg_len(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token2"],
        "og_message_id" : data["dm_message_id"],
        "message" : "f" * 1005,
        "channel_id":   data["channel_id"],
        "dm_id" : -1
    })
    assert response.status_code == INPUT_ERROR

#check if the message was actually sent
def test_message_share_verify_msg(data):
    #share a message
    response1 = requests.post(url + "message/share/v1", 
    json={
        "token":        data["token2"],
        "og_message_id" : data["dm_message_id"],
        "message" : "new msg",
        "channel_id":   data["channel_id"],
        "dm_id" : -1
    })
    assert response1.status_code == NO_ERROR

    #get messages from dm
    response2 = requests.get(url + "channel/messages/v2", 
    params={
        "token": data["token2"],
        "channel_id": data["channel_id"],
        "start": 0
    })
    messages = response2.json()["messages"]
    assert messages[0]["message"] == "hello from the other side new msg"
    assert messages[0]["u_id"] == data["user2_id"]
 
# testing invalid channel
def test_message_share_invalid_channel(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token2"],
        "og_message_id":    data["dm_message_id"],
        "message" :         "fuuuuuuu",
        "channel_id":       1381830,
        "dm_id" :           -1
    })
    assert response.status_code == INPUT_ERROR

# testing invalid dm
def test_message_share_invalid_dm(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token2"],
        "og_message_id":    data["dm_message_id"],
        "message" :         "fuuuuuuu",
        "channel_id":       -1,
        "dm_id" :           9281739
    })
    assert response.status_code == INPUT_ERROR

# testing user in dm
def test_message_share_user_in_dm(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token1"],
        "og_message_id":    data["dm_message_id"],
        "message" :         "fuuuuuuu",
        "channel_id":       -1,
        "dm_id" :           data["dm_id"]
    })
    assert response.status_code == NO_ERROR

# testing message in channel
def test_message_share_from_channel(data):
    response = requests.post(url + "message/share/v1", 
    json={
        "token":            data["token2"],
        "og_message_id":    data["channel_message_id"],
        "message" :         "fuuuuuuu",
        "channel_id":       -1,
        "dm_id" :           data["dm_id"]
    })
    assert response.status_code == NO_ERROR