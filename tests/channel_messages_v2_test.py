import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "channel/messages/v2"

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
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "public_channel_id":    public_channel_id,
        "private_channel_id":   private_channel_id
    }

# testing valid token, invalid channel_id
def test_channel_messages_v2_invalid_channel_id(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.get(URL, params={
        "token":        user1_token,
        "channel_id":   -34587678,
        "start":        0
    })
    assert response.status_code == INPUT_ERROR

# testing invalid token, valid public channel_id
def test_channel_messages_v2_invalid_token_public(initial_setup):
    public_channel = initial_setup["public_channel_id"]
    response = requests.get(URL, params={
        "token":        "kjkjd",
        "channel_id":   public_channel,
        "start":        0
    })
    assert response.status_code == ACCESS_ERROR

# testing invalid token, valid private channel_id
def test_channel_messages_v2_invalid_token_private(initial_setup):
    private_channel = initial_setup["private_channel_id"]
    response = requests.get(URL, params={
        "token":        "kjkjd",
        "channel_id":   private_channel,
        "start":        0
    })
    assert response.status_code == ACCESS_ERROR

# testing global user (not a member) trying to access valid channel
def test_channel_messages_v2_global_user_not_member(initial_setup):
    user0_token = initial_setup["user0_token"]
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.get(URL, params={
        "token":        user0_token,
        "channel_id":   public_channel,
        "start":        0
    })

    response2 = requests.get(URL, params={
        "token":        user0_token,
        "channel_id":   private_channel,
        "start":        0
    })

    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

# testing normal user (not a member) trying to access valid channel
def test_channel_messages_v2_unauthorised_user(initial_setup):
    user2_token = initial_setup["user2_token"]
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.get(URL, params={
        "token":        user2_token,
        "channel_id":   public_channel,
        "start":        0
    })

    response2 = requests.get(URL, params={
        "token":        user2_token,
        "channel_id":   private_channel,
        "start":        0
    })

    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

# token and channel_id both invalid
def test_channel_messages_v2_invalid_token_and_channel_id(initial_setup):
    response = requests.get(URL, params={
        "token":        "4534",
        "channel_id":   -45857,
        "start":        0
    })
    assert response.status_code == ACCESS_ERROR

# invalid start value only
def test_channel_messages_v2_invalid_start(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.get(URL, params={
        "token":        user1_token,
        "channel_id":   public_channel,
        "start":        498986984
    })
    assert response1.status_code == INPUT_ERROR

    response2 = requests.get(URL, params={
        "token":        user1_token,
        "channel_id":   private_channel,
        "start":        5897948576
    })
    assert response2.status_code == INPUT_ERROR

def test_channel_messages_v2_valid(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel = initial_setup["public_channel_id"]
    
    requests.post(url + "message/send/v1", json={
        "token": user1_token,
        "channel_id": public_channel,
        "message": "hi"
    })

    requests.post(url + "message/send/v1", json={
        "token": user1_token,
        "channel_id": public_channel,
        "message": "hi"
    })
    response1 = requests.get(URL, params={
        "token":        user1_token,
        "channel_id":   public_channel,
        "start": 0
    })
    assert response1.status_code == NO_ERROR

    data = response1.json()
    assert data["start"] == 0
    assert len(data["messages"]) == 2
    assert data["end"] == -1

def test_channel_messages_v2_valid2(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel = initial_setup["public_channel_id"]
    
    for i in range(51):
        requests.post(url + "message/send/v1", json={
            "token": user1_token,
            "channel_id": public_channel,
            "message": "hi" + str(i)
        })

    response1 = requests.get(URL, params={
        "token":        user1_token,
        "channel_id":   public_channel,
        "start": 0
    })
    assert response1.status_code == NO_ERROR

    data = response1.json()
    assert data["start"] == 0
    assert len(data["messages"]) == 50
    assert data["end"] == 50

def test_channel_messages_v2_valid3(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel = initial_setup["public_channel_id"]
    
    for i in range(50):
        requests.post(url + "message/send/v1", json={
            "token": user1_token,
            "channel_id": public_channel,
            "message": "hi" + str(i)
        })

    response1 = requests.get(URL, params={
        "token":        user1_token,
        "channel_id":   public_channel,
        "start": 0
    })
    assert response1.status_code == NO_ERROR

    data = response1.json()
    assert data["start"] == 0
    assert len(data["messages"]) == 50
    assert data["end"] == -1
