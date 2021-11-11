from src.config import url
from src.gen_timestamp import get_curr_timestamp
import json 
import requests
import pytest
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

# Make sure all user's stats are 0 at timestamp 0
def test_initial_stats(data):
    token1 = data["token1"]
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][0]["num_channels_joined"] == 0
    assert user_stats["dms_joined"][0]["num_dms_joined"] == 0
    assert user_stats["messages_sent"][0]["num_messages_sent"] == 0
    assert user_stats["involvement_rate"] == 0

# Check user's stats after they create a channel
def test_channels_create_stats(data):
    token1 = data["token1"]

    # create 1 channel
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # check user's stats after channel is creates
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][1]["num_channels_joined"] == 1

# Check user's stats after they join a channel
def test_channel_join_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

    # user1 create channel1
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # user2 joins channel1
    requests.post(url + "channel/join/v2", json={
        "token": token2,
        "channel_id": 0
    })

    # check user2's stats after joining channel
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][1]["num_channels_joined"] == 1

# Check user's stats after they are invited to a channel
def test_channel_invite_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

    # user1 create channel1
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # user1 invites user2 to channel1
    requests.post(url + "channel/invite/v2", json={
        "token": token1,
        "channel_id": 0,
        "u_id": 1
    })

    # check user2's stats after being invited to channel1
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][1]["num_channels_joined"] == 1

# Check user's stats after they leave a channel
def test_channel_leave_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

    # user1 create channel1
    requests.post(url + "channels/create/v2", json={
        "token": token1,
        "name": "channel1",
        "is_public": True
    })

    # user1 invites user2 to channel1
    requests.post(url + "channel/invite/v2", json={
        "token": token1,
        "channel_id": 0,
        "u_id": 1
    })

    # user2 leaves channel1
    requests.post(url + "channel/leave/v1", json={
        "token": token2,
        "channel_id": 0
    })

    # check user2's stats after leaving channel1
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][2]["num_channels_joined"] == 0

# Check user's stats after they create a dm
def test_dm_create_user1_stats(data):
    token1 = data["token1"]

    # user1 create dm1 with 1 user
    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": []
    })

    # check user's stats after creating dm1
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][1]["num_dms_joined"] == 1

# Check other user's stats after they were invited to dm
def test_dm_create_user2_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

    # user1 create dm1 with user2
    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1]
    })

    # check other users' stats after creating dm1
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][1]["num_dms_joined"] == 1

# Check stats of dm members when dm is removed
def test_dm_remove_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

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
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][2]["num_dms_joined"] == 0

    # check user2's stats after removing dm1
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][2]["num_dms_joined"] == 0

# Check stats of user after dm leave
def test_dm_leave_stats(data):
    token1 = data["token1"]
    token2 = data["token2"]

    # user1 create dm1 with user2
    requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1]
    })

    # remove dm
    requests.post(url + "dm/leave/v1", json={
        "token": token1,
        "dm_id": 0
    })

    # check user1's stats after leaving dm1
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][2]["num_dms_joined"] == 0

    # check user2's stats is the same
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][1]["num_dms_joined"] == 1

# Check user's stats after sending a message in a channel
def test_message_send_stats(data):
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
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][1]["num_channels_joined"] == 1
    assert user_stats["messages_sent"][1]["num_messages_sent"] == 1

# Check user's stats after sending a message in a dm
def test_message_senddm_stats(data):
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
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][1]["num_dms_joined"] == 1
    assert user_stats["messages_sent"][1]["num_messages_sent"] == 1

# Check user's stats after send later a message in a channel
def test_message_sendlater_stats(data):
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
    time.sleep(5)
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][1]["num_channels_joined"] == 1
    assert user_stats["messages_sent"][1]["num_messages_sent"] == 1

# Check user's stats after sending later a message in a dm
def test_message_sendlaterdm_stats(data):
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
    response = requests.get(url + "user/stats/v1", params={
        "token": token1
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["dms_joined"][1]["num_dms_joined"] == 1
    assert user_stats["messages_sent"][1]["num_messages_sent"] == 1

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

    # send a message to channel1
    requests.post(url + "message/send/v1", json={
        "token": token2,
        "channel_id": 0,
        "message": "okay"
    })

    # check user's stats after message is sent
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == NO_ERROR

    user_stats = response.json()["user_stats"]
    assert user_stats["channels_joined"][1]["num_channels_joined"] == 1
    assert user_stats["messages_sent"][1]["num_messages_sent"] == 1

    # have user1 remove user2 from streams
    requests.delete(url + "admin/user/remove/v1", json={
        "token": token1,
        "u_id": 1
    })

    # check user's stats after being removed
    response = requests.get(url + "user/stats/v1", params={
        "token": token2
    })
    assert response.status_code == ACCESS_ERROR