import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "message/remove/v1"

        # "user0_token":          user0_token,
        # "user1_token":          user1_token,
        # "user2_token":          user2_token,
        # "user2_id":             user2_id,
        # "message_id_public":    message_id_public,
        # "message_id_private":   message_id_private,
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

    return {
        "user0_token":          user0_token,
        "user0_id":             user0_id,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "user2_id":             user2_id,
        "message_id_public":    message_id_public,
        "message_id_private":   message_id_private,
        "public_channel_id":    public_channel_id,
        "private_channel_id":   private_channel_id
    }

# testing invalid token only
def test_message_remove_v1_invalid_token(initial_setup):
    message_id = initial_setup["message_id_public"][0]
    response = requests.delete(URL, json={
        "token":        "lalala",
        "message_id":   message_id,
    })
    assert response.status_code == ACCESS_ERROR

# testing invalid token and message_id
def test_message_remove_v1_invalid_token_and_message_id(initial_setup):
    response = requests.delete(URL, json={
        "token":        "lalala",
        "message_id":   -89,
    })
    assert response.status_code == ACCESS_ERROR

# testing valid message, user not in channel (duplicate test)
def test_message_remove_v1_invalid_message(initial_setup):
    user0_token = initial_setup["user0_token"]
    user2_token = initial_setup["user2_token"]
    message_id = initial_setup["message_id_public"][0]

    response = requests.delete(URL, json={
        "token":        user0_token,
        "message_id":   message_id,
    })
    assert response.status_code == INPUT_ERROR  

    response2 = requests.delete(URL, json={
        "token":        user2_token,
        "message_id":   message_id,
    })
    assert response2.status_code == INPUT_ERROR  

# testing valid token (user is a member), invalid message_id
def test_message_remove_v1_invalid_message_id(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.delete(URL, json={
        "token":        user1_token,
        "message_id":   -34587678
    })
    assert response.status_code == INPUT_ERROR

# testing global user (not a member), valid message_id
def test_message_remove_v1_global_user_not_member(initial_setup):
    user0_token = initial_setup["user0_token"]
    message_id1 = initial_setup["message_id_public"][1]
    message_id2 = initial_setup["message_id_private"][0]

    response1 = requests.delete(URL, json={
        "token":        user0_token,
        "message_id":   message_id1,
    })
    assert response1.status_code == INPUT_ERROR

    response2 = requests.delete(URL, json={
        "token":        user0_token,
        "message_id":   message_id2,
    })
    assert response2.status_code == INPUT_ERROR

# testing normal user (not a member), valid message_id and message
def test_message_remove_v1_unauthorised_user(initial_setup):
    user2_token = initial_setup["user2_token"]
    message_id1 = initial_setup["message_id_public"][2]
    message_id2 = initial_setup["message_id_private"][1]

    response1 = requests.delete(URL, json={
        "token":        user2_token,
        "message_id":   message_id1,
    })
    assert response1.status_code == INPUT_ERROR

    response2 = requests.delete(URL, json={
        "token":        user2_token,
        "message_id":   message_id2,
    })
    assert response2.status_code == INPUT_ERROR

# testing member of channel (not owner), all else valid
def test_message_remove_v1_user_not_owner(initial_setup):
    user1_token = initial_setup["user1_token"]
    user2_id = initial_setup["user2_id"]
    public_channel_id = initial_setup["public_channel_id"]
    private_channel_id = initial_setup["private_channel_id"]

    user2_token = initial_setup["user2_token"]
    message_id1 = initial_setup["message_id_public"][2]
    message_id2 = initial_setup["message_id_private"][1]

    response1 = requests.post(f"{url}channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   public_channel_id,
        "u_id":         user2_id
    })
    assert response1.status_code == NO_ERROR

    response2 = requests.post(f"{url}channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   private_channel_id,
        "u_id":         user2_id
    })
    assert response2.status_code == NO_ERROR

    response3 = requests.delete(URL, json={
        "token":        user2_token,
        "message_id":   message_id1,
    })
    assert response3.status_code == ACCESS_ERROR

    response4 = requests.delete(URL, json={
        "token":        user2_token,
        "message_id":   message_id2,
    })
    assert response4.status_code == ACCESS_ERROR

# testing global owner (member of channel) deleting non own messages
def test_message_remove_v1_global_user_messages(initial_setup):
    user1_token = initial_setup["user1_token"]
    user0_id = initial_setup["user0_id"]
    public_channel_id = initial_setup["public_channel_id"]
    private_channel_id = initial_setup["private_channel_id"]

    user0_token = initial_setup["user0_token"]
    message_id1 = initial_setup["message_id_public"][2]
    message_id2 = initial_setup["message_id_private"][1]

    response1 = requests.post(f"{url}channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   public_channel_id,
        "u_id":         user0_id
    })
    assert response1.status_code == NO_ERROR

    response2 = requests.post(f"{url}channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   private_channel_id,
        "u_id":         user0_id
    })
    assert response2.status_code == NO_ERROR

    response3 = requests.delete(URL, json={
        "token":        user0_token,
        "message_id":   message_id1,
    })
    assert response3.status_code == NO_ERROR

    response4 = requests.delete(URL, json={
        "token":        user0_token,
        "message_id":   message_id2,
    })
    assert response4.status_code == NO_ERROR

# testing normal user (member of channel) deleting own messages
def test_message_remove_v1_normal_user_messages(initial_setup):
    user1_token = initial_setup["user1_token"]
    user2_id = initial_setup["user2_id"]
    public_channel_id = initial_setup["public_channel_id"]
    private_channel_id = initial_setup["private_channel_id"]
    user2_token = initial_setup["user2_token"]

    response1 = requests.post(f"{url}channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   public_channel_id,
        "u_id":         user2_id
    })
    assert response1.status_code == NO_ERROR

    response2 = requests.post(f"{url}channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   private_channel_id,
        "u_id":         user2_id
    })
    assert response2.status_code == NO_ERROR

    message1_id = -1
    message2_id = -2

    response3 = requests.post(f"{url}message/send/v1", json={
        "token":        user2_token,
        "channel_id":   public_channel_id,
        "message":      "what did the fox say?"
    })
    data3 = response3.json()
    message1_id = data3["message_id"]

    response4 = requests.post(f"{url}message/send/v1", json={
        "token":        user2_token,
        "channel_id":   private_channel_id,
        "message":      "Vocalise"
    })
    data4 = response4.json()
    message2_id = data4["message_id"]

    response5 = requests.delete(URL, json={
        "token":        user2_token,
        "message_id":   message1_id,
    })
    assert response5.status_code == NO_ERROR

    response6 = requests.delete(URL, json={
        "token":        user2_token,
        "message_id":   message2_id,
    })
    assert response6.status_code == NO_ERROR

    response = requests.get(url + "channel/messages/v2", params={
        "token":        user2_token,
        "channel_id":   private_channel_id,
        "start":        0
    })
    assert response.status_code == NO_ERROR
    assert len(response.json()["messages"]) == 3
