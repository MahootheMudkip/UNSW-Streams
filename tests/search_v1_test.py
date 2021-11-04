import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "search/v1"

        # "user0_token":          user0_token,
        # "user0_id":             user0_id,
        # "user1_token":          user1_token,
        # "user2_token":          user2_token,
        # "user2_id":             user2_id,
        # "message_id_public":    message_id_public,
        # "message_id_private":   message_id_private,
        # "public_channel_id":    public_channel_id,
        # "private_channel_id":   private_channel_id,
        # "dm_messages":          dm_messages,
        # "dm_id1":               dm_id1

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
    assert user1_response.status_code == NO_ERROR
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

    message_id_public = []
    message_id_private = []

    for i in range(3):
        response = requests.post(f"{url}message/send/v1", json={
            "token":        user1_token,
            "channel_id":   public_channel_id,
            "message":      f"Hello there! I am message {i}!"
        })
        assert response.status_code == NO_ERROR
        data = response.json()
        message_id_public.append(data["message_id"])
    
    for j in range(3):
        response = requests.post(f"{url}message/send/v1", json={
            "token":        user1_token,
            "channel_id":   private_channel_id,
            "message":      f"Bye! I am message {j}!"
        })
        assert response.status_code == NO_ERROR
        data = response.json()
        message_id_private.append(data["message_id"])

    response = requests.post(url + "dm/create/v1", json={
        "token":    user1_token,
        "u_ids":    [0, 2]
        })
    assert response.status_code == NO_ERROR
    dm_id1 = response.json()["dm_id"]

    dm_messages = []
    for j in range(3):
        response = requests.post(f"{url}message/senddm/v1", json={
            "token":        user1_token,
            "dm_id":        dm_id1,
            "message":      f"This is chicken dm msg {j}"
        })
        assert response.status_code == NO_ERROR
        data = response.json()
        dm_messages.append(data["message_id"])
        
    return {
        "user0_token":          user0_token,
        "user0_id":             user0_id,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "user2_id":             user2_id,
        "message_id_public":    message_id_public,
        "message_id_private":   message_id_private,
        "public_channel_id":    public_channel_id,
        "private_channel_id":   private_channel_id,
        "dm_messages":          dm_messages,
        "dm_id1":               dm_id1
    }

# invalid token only
def test_search_v1_invalid_token(initial_setup):
    resp = requests.get(URL, params={
        "token":        "faker",
        "query_str":    "sdf"
    })
    assert resp.status_code == ACCESS_ERROR

# invalid query string given
def test_search_v1_invalid_query_string(initial_setup):
    user0_token = initial_setup["user0_token"]

    resp = requests.get(URL, params={
        "token":        user0_token,
        "query_str":    ""
    })
    assert resp.status_code == INPUT_ERROR

    resp = requests.get(URL, params={
        "token":        user0_token,
        "query_str":    "a" * 1001
    })
    assert resp.status_code == INPUT_ERROR

# valid, user has not sent any messages
def test_search_v1_no_msgs_sent(initial_setup):
    user0_token = initial_setup["user0_token"]

    resp = requests.get(URL, params={
        "token":        user0_token,
        "query_str":    "ddfs"
    })
    assert resp.status_code == NO_ERROR
    assert len(resp.json()["messages"]) == 0

    resp = requests.get(URL, params={
        "token":        user0_token,
        "query_str":    "a"
    })
    assert resp.status_code == NO_ERROR
    assert len(resp.json()["messages"]) == 0

# valid, user has not sent messages in both dm and channels
def test_search_v1_msgs_sent(initial_setup):
    user1_token = initial_setup["user1_token"]

    resp = requests.get(URL, params={
        "token":        user1_token,
        "query_str":    "I am message"
    })
    assert resp.status_code == NO_ERROR
    assert len(resp.json()["messages"]) == 6

    resp = requests.get(URL, params={
        "token":        user1_token,
        "query_str":    "chicken"
    })
    assert resp.status_code == NO_ERROR
    assert len(resp.json()["messages"]) == 3

    resp = requests.get(URL, params={
        "token":        user1_token,
        "query_str":    "m"
    })
    assert resp.status_code == NO_ERROR
    assert len(resp.json()["messages"]) == 9