from src.config import url
import json 
import requests
import pytest
import time
from src.gen_timestamp import get_curr_timestamp
import time

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

    values = {
        "token1": token1,
        "token2": token2
    }

    return values

# Make sure all workspace stats are 0 at data entry 0
def test_initial_workspace_stats(data):
    token1 = data["token1"]
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][0]["num_channels_exist"] == 0
    assert workspace_stats["dms_exist"][0]["num_dms_exist"] == 0
    assert workspace_stats["messages_exist"][0]["num_messages_exist"] == 0
    assert workspace_stats["utilization_rate"] == 0

# Check workspace stats after user creates a channel
def test_channels_create_workspace_stats(data):
    token1 = data["token1"]

    # create 1 channel
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # check user's stats after channel is creates
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][1]["num_channels_exist"] == 1

# Check workspace stats after user creates a dm
def test_dm_create_workspace_stats(data):
    token1 = data["token1"]

    # user1 create dm1 with 1 user
    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": []
    })

    # check user's stats after creating dm1
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][1]["num_dms_exist"] == 1

# Check stats of dm members when dm is removed
def test_dm_remove_workspace_stats(data):
    token1 = data["token1"]

    # user1 create dm1 with user2
    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1]
    })

    # remove dm
    requests.delete(url + "dm/remove/v1", json={
        "token": token1,
        "dm_id": 0
    })

    # check user1's stats after removing dm1
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][2]["num_dms_exist"] == 0

# Check user's stats after sending a message in a channel
def test_message_send_workspace_stats(data):
    token1 = data["token1"]

    # create 1 channel
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # send a message to channel1
    requests.post(url + "message/send/v1", json={
        "token": token1,
        "channel_id": 0,
        "message": "okay"
    })

    # check user's stats after message is sent
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][1]["num_channels_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1

# Check user's stats after sending a message in a dm
def test_message_senddm_workspace_stats(data):
    token1 = data["token1"]

    # user1 create dm1 with 1 user
    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": []
    })

    # user1 send message to dm
    requests.post(url + "message/senddm/v1", json={
        "token": token1,
        "dm_id": 0,
        "message": "hello"
    })

    # check user's stats after message is sent
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][1]["num_dms_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1

# Check user's stats after send later a message in a channel
def test_message_sendlater_workspace_stats(data):
    token1 = data["token1"]

    # create 1 channel
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # send later a message to channel1
    timestamp = get_curr_timestamp()
    requests.post(url + "message/sendlater/v1", json={
        "token": token1,
        "channel_id": 0,
        "message": "okay",
        "time_sent": timestamp + 1
    })

    # check user's stats after message is sent
    time.sleep(1)
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["channels_exist"][1]["num_channels_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1

# Check user's stats after sending later a message in a dm
def test_message_sendlaterdm_workspace_stats(data):
    token1 = data["token1"]

    # user1 create dm1 with 1 user
    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": []
    })

    # send later a message to channel1
    timestamp = get_curr_timestamp()
    requests.post(url + "message/sendlaterdm/v1", json={
        "token": token1,
        "dm_id": 0,
        "message": "hello",
        "time_sent": timestamp + 1
    })

    # check user's stats after sending message to dm
    time.sleep(1)
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["dms_exist"][1]["num_dms_exist"] == 1
    assert workspace_stats["messages_exist"][1]["num_messages_exist"] == 1

# Check user's stats after they are removed from streams
def test_user_remove_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

    # create 1 channel
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # user2 joins channel1
    requests.post(url + "channel/join/v2", json={
        "token": token2,
        "channel_id": 0,
    })

    # have user1 remove user2 from streams
    requests.delete(url + "admin/user/remove/v1", json={
        "token": token1,
        "u_id": 1
    })

    # check user's stats after they are removed
    response = requests.get(url + "users/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    workspace_stats = response.json()["workspace_stats"]
    assert workspace_stats["utilization_rate"] == 1