from src.config import url
import json 
import requests
import pytest

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

    # create a channel 
    response = requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": False
    })
    channel_id = response.json()["channel_id"]

    values = {
        "token1": token1,
        "token2": token2,
        "channel_id": channel_id,
    }

    return values

# notification sent when user is added to channel
def test_notifications_added_to_channel(data):
    token1 = data["token1"]
    token2 = data["token2"]
    channel_id = data["channel_id"]

    requests.post(url + "channel/invite/v2", json={
        "token":        token1,
        "channel_id":   channel_id,
        "u_id":         1
    })
    
    response = requests.get(url + "notifications/get/v1", params={
        "token":        token2
    })
    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][0]["channel_id"] == channel_id
    assert response.json()["notifications"][0]["dm_id"] == -1
    assert response.json()["notifications"][0]["notification_message"] == "lukepierce added you to channel1"

# notification sent when user is added to dm
def test_notifications_added_to_dm(data):
    token1 = data["token1"]
    token2 = data["token2"]

    response = requests.post(url + "dm/create/v1", json={
        "token":        token1,
        "u_ids":        [1]
    })
    dm_id = response.json()["dm_id"]

    response = requests.get(url + "notifications/get/v1", params={
        "token":        token2
    })
    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][0]["channel_id"] == -1
    assert response.json()["notifications"][0]["dm_id"] == dm_id
    assert response.json()["notifications"][0]["notification_message"] == "lukepierce added you to artemwing, lukepierce"

# notification sent when user is tagged in a channel message
def test_notifications_tagged_in_channel_msg(data):
    token1 = data["token1"]
    token2 = data["token2"]
    channel_id = data["channel_id"]

    requests.post(url + "channel/invite/v2", json={
        "token":        token1,
        "channel_id":   channel_id,
        "u_id":         1
    })

    requests.post(url + "message/send/v1", json={
        "token":        token1,
        "channel_id":   channel_id,
        "message":      "Hello @artemwing, welcome to the channel!"
    })
    
    response = requests.get(url + "notifications/get/v1", params={
        "token":        token2
    })
    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][0]["channel_id"] == channel_id
    assert response.json()["notifications"][0]["dm_id"] == -1
    assert response.json()["notifications"][0]["notification_message"] == "lukepierce tagged you in channel1: Hello @artemwing, we"

# notification sent when user is tagged in a dm message 
def test_notifications_tagged_in_dm_msg(data):
    token1 = data["token1"]
    token2 = data["token2"]

    response = requests.post(url + "dm/create/v1", json={
        "token":        token1,
        "u_ids":        [1]
    })
    dm_id = response.json()["dm_id"]

    requests.post(url + "message/senddm/v1", json={
        "token":        token1,
        "dm_id":        dm_id,
        "message":      "Hello @artemwing, welcome to the dm!"
    })
    
    response = requests.get(url + "notifications/get/v1", params={
        "token":        token2
    })
    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][0]["channel_id"] == -1
    assert response.json()["notifications"][0]["dm_id"] == dm_id
    assert response.json()["notifications"][0]["notification_message"] == "lukepierce tagged you in artemwing, lukepierce: Hello @artemwing, we"

# notification sent when user's channel message has been reacted
def test_notifications_reacted_in_channel_msg(data):
    token1 = data["token1"]
    token2 = data["token2"]
    channel_id = data["channel_id"]

    requests.post(url + "channel/invite/v2", json={
        "token":        token1,
        "channel_id":   channel_id,
        "u_id":         1
    })

    requests.post(url + "message/send/v1", json={
        "token":        token2,
        "channel_id":   channel_id,
        "message":      "Pls react to this!"
    })

    requests.post(url + "message/react/v1", json={
        "token":        token1,
        "message_id":   0,
        "react_id":     1
    })
    
    response = requests.get(url + "notifications/get/v1", params={
        "token":        token2
    })
    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][0]["channel_id"] == channel_id
    assert response.json()["notifications"][0]["dm_id"] == -1
    assert response.json()["notifications"][0]["notification_message"] == "lukepierce reacted to your message in channel1"

# notification sent when user's dm message has been reacted
def test_notifications_reacted_in_dm_msg(data):
    token1 = data["token1"]
    token2 = data["token2"]

    response = requests.post(url + "dm/create/v1", json={
        "token":        token1,
        "u_ids":        [1]
    })
    dm_id = response.json()["dm_id"]

    requests.post(url + "message/senddm/v1", json={
        "token":        token2,
        "dm_id":        dm_id,
        "message":      "Pls react to this!"
    })

    requests.post(url + "message/react/v1", json={
        "token":        token1,
        "message_id":   0,
        "react_id":     1
    })
    
    response = requests.get(url + "notifications/get/v1", params={
        "token":        token2
    })
    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][0]["channel_id"] == -1
    assert response.json()["notifications"][0]["dm_id"] == dm_id
    assert response.json()["notifications"][0]["notification_message"] == "lukepierce reacted to your message in artemwing, lukepierce"

# list of notifications of a user are returned in the correct order
def test_notifications_list_of_notications(data):
    token1 = data["token1"]
    token2 = data["token2"]
    channel_id = data["channel_id"]

    requests.post(url + "channel/invite/v2", json={
        "token":        token1,
        "channel_id":   channel_id,
        "u_id":         1
    })

    requests.post(url + "message/send/v1", json={
        "token":        token1,
        "channel_id":   channel_id,
        "message":      "Hello @artemwing, welcome to the channel!"
    })

    requests.post(url + "message/send/v1", json={
        "token":        token2,
        "channel_id":   channel_id,
        "message":      "Hello luke!"
    })

    requests.post(url + "message/react/v1", json={
        "token":        token1,
        "message_id":   1,
        "react_id":     1
    })
    
    response = requests.get(url + "notifications/get/v1", params={
        "token":        token2
    })
    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][0]["channel_id"] == channel_id
    assert response.json()["notifications"][0]["dm_id"] == -1
    assert response.json()["notifications"][0]["notification_message"] == "lukepierce reacted to your message in channel1"

    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][1]["channel_id"] == channel_id
    assert response.json()["notifications"][1]["dm_id"] == -1
    assert response.json()["notifications"][1]["notification_message"] == "lukepierce tagged you in channel1: Hello @artemwing, we"

    assert response.status_code == NO_ERROR
    assert response.json()["notifications"][2]["channel_id"] == channel_id
    assert response.json()["notifications"][2]["dm_id"] == -1
    assert response.json()["notifications"][2]["notification_message"] == "lukepierce added you to channel1"