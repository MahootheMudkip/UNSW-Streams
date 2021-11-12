from src import dm
import pytest
import requests
import json
from src.config import url
import re
from src.user import *

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

    #create a dm
    response = requests.post(url + "dm/create/v1", 
    json={
        "token": token1,
        "u_ids": []
    })
    dm_id = response.json()["dm_id"]

    #create a channel
    channel_response = requests.post(url + "channels/create/v2", 
    json={
        "token":        token1,
        "name":         "Jennifer garner",
        "is_public":    True
    })
    assert channel_response.status_code == NO_ERROR
    channel_id = channel_response.json()["channel_id"]
    
    #send a message in the channel
    channel_msg_resp = requests.post(url + "message/send/v1", 
    json={
        "token": token1,
        "channel_id": channel_id,
        "message": "Send this message or you die"
    })
    assert channel_msg_resp.status_code == NO_ERROR
    channel_message_id = channel_msg_resp.json()["message_id"]

    #send a message in the dm
    dm_msg_resp = response = requests.post(url + "message/senddm/v1", 
    json={
        "token":        token1,
        "dm_id":        dm_id,
        "message":      "hello from the other side"
    })
    assert dm_msg_resp.status_code == NO_ERROR
    dm_message_id = dm_msg_resp.json()["message_id"]

    return {
        "token1": token1,
        "dm_id": dm_id,
        "channel_id" : channel_id,
        "channel_message_id" : channel_message_id,
        "dm_message_id" : dm_message_id
    }

def test_handle_in_channel(data):
    with pytest.raises(Exception):
        channel_id = data["channel_id"]
        handle_in_channel("kekw", channel_id)

def test_handle_in_dm(data):
    with pytest.raises(Exception):
        dm_id = data["dm_id"]
        handle_in_channel("kekw", dm_id)

def test_to_uid():
    to_uid("kekw")

def test_find_location():
    find_location(93819)