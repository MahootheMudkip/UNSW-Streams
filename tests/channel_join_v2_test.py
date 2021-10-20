import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "channel/join/v2"

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
    user2_id = user2["auth_user_id"]

    # create new user 3 and extract token
    user3_response = requests.post(auth_register_url, json={      
        "email":        "pwd@gmail.com",
        "password":     "456789",
        "name_first":   "Richard",
        "name_last":    "Hammond"
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
        "name":         "private_channel",
        "is_public":    False
    })
    private_channel = private_channel_response.json()
    private_channel_id = private_channel["channel_id"]

    return {
        "user0_token":          user0_token,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "user2_id":             user2_id,
        "user3_token":          user3_token,
        "public_channel_id":    public_channel_id,
        "private_channel_id":   private_channel_id
    }

# testing invalid channel_id only
def test_channel_join_v2_invalid_channel_only(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   -34
    })
    assert response.status_code == INPUT_ERROR

# testing private channel and user not already in channel
def test_channel_join_v2_unauthorised_user(initial_setup):
    user2_token = initial_setup["user2_token"]
    user3_token = initial_setup["user3_token"]
    private_channel = initial_setup["private_channel_id"]
    response1 = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   private_channel
    })
    response2 = requests.post(URL, json={
        "token":        user3_token,
        "channel_id":   private_channel
    })
    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

# testing user (owner) already in public channel
def test_channel_join_v2_already_in_public_channel_owner(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel = initial_setup["public_channel_id"]
    response = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   public_channel
    })
    assert response.status_code == INPUT_ERROR

# testing user (owner) already in private channel
def test_channel_join_v2_already_in_private_channel_owner(initial_setup):
    user1_token = initial_setup["user1_token"]
    private_channel = initial_setup["private_channel_id"]
    response = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   private_channel
    })
    assert response.status_code == INPUT_ERROR

# testing user already in public channel
def test_channel_join_v2_already_in_public_channel(initial_setup):
    user3_token = initial_setup["user3_token"]
    public_channel = initial_setup["public_channel_id"]
    response1 = requests.post(URL, json={
        "token":        user3_token,
        "channel_id":   public_channel
    })
    assert response1.status_code == NO_ERROR
    response2 = requests.post(URL, json={
        "token":        user3_token,
        "channel_id":   public_channel
    })
    assert response2.status_code == INPUT_ERROR

# testing user already in private channel
def test_channel_join_v2_already_in_private_channel(initial_setup):
    user2_token = initial_setup["user2_token"]
    user1_token = initial_setup["user1_token"]
    user2_id = initial_setup["user2_id"]
    private_channel = initial_setup["private_channel_id"]

    invite_response = requests.post(url + "channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   private_channel,
        "u_id":         user2_id 
    })
    assert invite_response.status_code == NO_ERROR

    response2 = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   private_channel
    })
    assert response2.status_code == INPUT_ERROR

# testing adding two users to public channel
def test_channel_join_v2_adding_users(initial_setup):
    user2_token = initial_setup["user2_token"]
    user3_token = initial_setup["user3_token"]
    public_channel = initial_setup["public_channel_id"]

    join_response1 = requests.post(URL, json={
        "token":        user3_token,
        "channel_id":   public_channel
    })
    assert join_response1.status_code == NO_ERROR
    details_response1 = requests.get(url + "channel/details/v2", params={
        "token":        user3_token,
        "channel_id":   public_channel
    })
    assert details_response1.status_code == NO_ERROR

    details1 = details_response1.json()
    assert details1["name"] == "public_channel"
    assert details1["is_public"] == True
    assert len(details1["all_members"]) == 2
    assert len(details1["owner_members"]) == 1

    join_response2 = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   public_channel
    })
    assert join_response2.status_code == NO_ERROR
    details_response2 = requests.get(url + "channel/details/v2", params={
        "token":        user2_token,
        "channel_id":   public_channel
    })
    assert details_response2.status_code == NO_ERROR
    details2 = details_response2.json()
    assert details2["name"] == "public_channel"
    assert details2["is_public"] == True
    assert len(details2["all_members"]) == 3
    assert len(details2["owner_members"]) == 1

# invalid token, valid channel_id
def test_channel_join_v2_invalid_token_only(initial_setup):
    private_channel = initial_setup["private_channel_id"]
    public_channel = initial_setup["public_channel_id"]
    response1 = requests.post(URL, json={
        "token":        -117,
        "channel_id":   public_channel
    })
    assert response1.status_code == ACCESS_ERROR
    response2 = requests.post(URL, json={
        "token":        -343,
        "channel_id":   private_channel
    })
    assert response2.status_code == ACCESS_ERROR

# invalid token, invalid channel_id
def test_channel_join_v2_invalid_token_and_channel(initial_setup):
    response1 = requests.post(URL, json={
        "token":        -117,
        "channel_id":   -777
    })
    assert response1.status_code == ACCESS_ERROR

# user already in private channel, but is not an owner
def test_channel_join_v2_user_in_private_channel_and_not_owner(initial_setup):
    private_channel = initial_setup["private_channel_id"]
    user1_token = initial_setup["user1_token"]
    user2_token = initial_setup["user2_token"]
    user2_id = initial_setup["user2_id"]
    invite_response = requests.post(url + "channel/invite/v2", json={
        "token":        user1_token,
        "channel_id":   private_channel,
        "u_id":         user2_id 
    })
    assert invite_response.status_code == NO_ERROR
    join_response = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   private_channel
    })
    assert join_response.status_code == INPUT_ERROR

# testing when user is a global user and is trying to join 
# public and private channel; this shouldn't have any errors
def test_channel_join_v2_global_user(initial_setup):
    user0_token = initial_setup["user0_token"]
    user1_token = initial_setup["user1_token"]
    private_channel = initial_setup["private_channel_id"]
    public_channel = initial_setup["public_channel_id"]

    # public channel test
    join_response1 = requests.post(URL, json={
        "token":        user0_token,
        "channel_id":   public_channel
    })
    assert join_response1.status_code == NO_ERROR

    details_response1 = requests.get(url + "channel/details/v2", params={
        "token":        user1_token,
        "channel_id":   public_channel
    })
    assert details_response1.status_code == NO_ERROR

    details1 = details_response1.json()
    assert details1["name"] == "public_channel"
    assert details1["is_public"] == True
    assert len(details1["all_members"]) == 2
    assert len(details1["owner_members"]) == 1

    # private channel test
    join_response2 = requests.post(URL, json={
        "token":        user0_token,
        "channel_id":   private_channel
    })
    assert join_response2.status_code == NO_ERROR

    details_response2 = requests.get(url + "channel/details/v2", params={
        "token":        user1_token,
        "channel_id":   private_channel
    })
    assert details_response2.status_code == NO_ERROR

    details2 = details_response2.json()
    assert details2["name"] == "private_channel"
    assert details2["is_public"] == False
    assert len(details2["all_members"]) == 2
    assert len(details2["owner_members"]) == 1

