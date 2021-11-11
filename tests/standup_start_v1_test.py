import pytest
import requests
from src.config import url
import json
from src.gen_timestamp import get_curr_timestamp

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "standup/start/v1"

        # "user0_token":          user0_token,
        # "user1_token":          user1_token,
        # "user2_token":          user2_token,
        # "user2_id":             user2_id,
        # "public_channel_id":    public_channel_id,
        # "private_channel_id":   private_channel_id

@pytest.fixture
def initial_setup():
    # clear all stored data
    requests.delete(url + "clear/v1")

    # url routes
    auth_register_url = url + "auth/register/v2"
    channel_create_url = url + "channels/create/v2"

    # create new user 0, (global owner) and extracts token
    user0_response = requests.post(auth_register_url, json={      
        "email":        "theboss@gmail.com", 
        "password":     "999999",
        "name_first":   "Big", 
        "name_last":    "Boss"
    })
    user0 = user0_response.json()
    user0_token = user0["token"]
    user0_id = user0["auth_user_id"]

    # create new user 1 and extract token
    user1_response = requests.post(auth_register_url, json={      
        "email":        "lmao@gmail.com", 
        "password":     "123789",
        "name_first":   "Jeremy", 
        "name_last":    "Clarkson"
    })
    user1 = user1_response.json()
    user1_token = user1["token"]

    # create new user 2 and extract token
    user2_response = requests.post(auth_register_url, json={      
        "email":        "wtf@gmail.com", 
        "password":     "234789",
        "name_first":   "James",
        "name_last":    "May"
    })
    user2 = user2_response.json()
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]

    # create new user 3 and extract token
    user3_response = requests.post(auth_register_url, json={      
        "email":        "wt@gmail.com", 
        "password":     "234789",
        "name_first":   "Jame",
        "name_last":    "Ma"
    })
    user3 = user3_response.json()
    user3_token = user3["token"]

    # create public channel and extract channel_id
    public_channel_response = requests.post(channel_create_url, json={
        "token":        user1_token,
        "name":         "public_channel",
        "is_public":    True
    })
    public_channel = public_channel_response.json()
    public_channel_id = public_channel["channel_id"]

    # create private channel and extract channel_id
    private_channel_response = requests.post(channel_create_url, json={
        "token":        user1_token,
        "name":         "public_channel",
        "is_public":    False
    })
    private_channel = private_channel_response.json()
    private_channel_id = private_channel["channel_id"]

    return {
        "user0_token":          user0_token,
        "user0_id":             user0_id,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "user3_token":          user3_token,
        "user2_id":             user2_id,
        "public_channel_id":    public_channel_id,
        "private_channel_id":   private_channel_id,
    }

# test invalid channel
def test_invalid_channel(initial_setup):
    user1_token = initial_setup["user1_token"]
    resp = requests.post(URL, json={"token": user1_token, "channel_id": 3332, "length": 120})
    assert(resp.status_code == INPUT_ERROR)

# the authorised user is not a member of the public channel
def test_auth_user_not_in_public_channel(initial_setup):
    user2_token = initial_setup["user2_token"]
    user3_token = initial_setup["user3_token"]
    public_channel_id = initial_setup["public_channel_id"]
    resp = requests.post(URL, json={"token": user2_token, "channel_id": public_channel_id, "length": 60})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(URL, json={"token": user3_token, "channel_id": public_channel_id, "length": 120})
    assert(resp2.status_code == ACCESS_ERROR)

# test user is invalid and public channel is valid
def test_user_invalid_and_public_channel_valid(initial_setup):
    public_channel_id = initial_setup["public_channel_id"]
    resp = requests.post(URL, json={"token": 4345, "channel_id": public_channel_id, "length": 180})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(URL, json={"token": 1521, "channel_id": public_channel_id, "length": 60})
    assert(resp2.status_code == ACCESS_ERROR)

# the authorised user is not a member of the channel and channel_id is invalid
def test_user_not_in_channel_and_invalid_channel_id(initial_setup):
    user2_token = initial_setup["user2_token"]
    resp = requests.post(URL, json={"token": user2_token, "channel_id": 5647, "length": 240})
    assert(resp.status_code == INPUT_ERROR)
    resp2 = requests.post(URL, json={"token": user2_token, "channel_id": 3231, "length": 240})
    assert(resp2.status_code == INPUT_ERROR)

# the authorised user is invalid and channel_id is invalid
def test_invalid_user_and_channel_id(initial_setup):
    resp = requests.post(URL, json={"token": 4332, "channel_id": 1521, "length": 60})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(URL, json={"token": 1542, "channel_id": 5551, "length": 120})
    assert(resp2.status_code == ACCESS_ERROR)

# test invalid length, all else valid
def test_invalid_length(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel_id = initial_setup["public_channel_id"]
    
    resp = requests.post(URL, json={"token": user1_token, "channel_id": public_channel_id, "length": -100})
    assert(resp.status_code == INPUT_ERROR)

    resp = requests.post(URL, json={"token": user1_token, "channel_id": public_channel_id, "length": -1})
    assert(resp.status_code == INPUT_ERROR)

# test standup already active
def test_already_active_standup_in_channel(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel_id = initial_setup["public_channel_id"]
    private_channel_id = initial_setup["private_channel_id"]
    
    resp = requests.post(URL, json={"token": user1_token, "channel_id": public_channel_id, "length": 1})
    assert(resp.status_code == NO_ERROR)

    resp = requests.post(URL, json={"token": user1_token, "channel_id": public_channel_id, "length": 1})
    assert(resp.status_code == INPUT_ERROR)

    resp = requests.post(URL, json={"token": user1_token, "channel_id": private_channel_id, "length": 1})
    assert(resp.status_code == NO_ERROR)

    resp = requests.post(URL, json={"token": user1_token, "channel_id": private_channel_id, "length": 1})
    assert(resp.status_code == INPUT_ERROR)

# test standup/start returns correct unix timestamp
def test_standup_start_v1_returns_time_finish(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel_id = initial_setup["public_channel_id"]
    
    resp = requests.post(URL, json={"token": user1_token, "channel_id": public_channel_id, "length": 1})
    assert(resp.status_code == NO_ERROR)

    time_finish = json.loads(resp.text)["time_finish"]
    curr_timestamp = get_curr_timestamp()
    assert time_finish == curr_timestamp + 1

