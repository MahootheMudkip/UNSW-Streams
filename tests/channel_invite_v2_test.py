from json.decoder import JSONDecodeError
import pytest
import requests
import json

from src import config, data_store
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1

# fixture for registering and logging in user to avoid repetition.
@pytest.fixture
def initial_data():
    # clear used data
    clear_v1()
    # Register first user
    user1_response = requests.post(config.url + 'auth/register/v2', data={
        "email": "daniel.ricc@gmail.com", 
        "password": "27012003", 
        "name_first": "Daniel", 
        "name_last": "Ricciardo"
    })
    user1 = json.loads(user1_response.text)
    user1_token = user1["token"]
    # Register second user
    user2_response = requests.post(config.url + 'auth/register/v2', data={
        "email": "lando.norris@gmail.com", 
        "password": "27012003", 
        "name_first": "Lando", 
        "name_last": "Norris"
    })
    user2 = json.loads(user2_response.text)
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    # Register third user
    user3_response = requests.post(config.url + 'auth/register/v2', data={
        "email": "mick.fanning@gmail.com", 
        "password": "27012003", 
        "name_first": "Mick", 
        "name_last": "Fanning"
    })
    user3 = json.loads(user3_response.text)
    user3_id = user3["auth_user_id"]
    # Make public channel
    public_channel_response = requests.post(config.url + 'channels/create/v2', data={
        "token": user1_token,
        "name": "Rainbow Six Siege",
        "is_public": True
    })
    public_channel = json.loads(public_channel_response.text)
    public_channel_id = public_channel["channel_id"]
    # Make private channel
    private_channel_response = requests.post(config.url + 'channels/create/v2', data={
        "token": user1_token,
        "name": "Minecraft",
        "is_public": False
    })
    private_channel = json.loads(private_channel_response)
    private_channel_id = private_channel["channel_id"]
    
    values = {
        "user1_token": user1_token,
        "user2_token": user2_token,
        "user2_id": user2_id,
        "user3_id": user3_id,
        "public_channel_id": public_channel_id,
        "private_channel_id": private_channel_id
    }
    return values

# channel_id does not refer to a valid channel. token and u_id are both valid.
def test_invalid_channel_only(initial_data):
    user1_token = initial_data["user1_token"]
    user2_id = initial_data["user2_id"]
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": user1_token, "channel_id": 1747, "u_id": user2_id})
    assert(resp.status_code == 400)

# u_id does not refer to a valid user. token and channel_id are both valid.
def test_invalid_u_id_only(initial_data):
    user1_token = initial_data["user1_token"]
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": user1_token, "channel_id": public_channel_id, "u_id": 7775})
    assert(resp.status_code == 400)  

# token does not refer to a valid user. channel_id and u_id are both valid
def test_invalid_token_only(initial_data):
    user2_id = initial_data["user2_id"]
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": 7773, "channel_id": public_channel_id, "u_id": user2_id})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/invite/v2', params={"token": 532, "channel_id": public_channel_id, "u_id": user2_id})
    assert(resp2.status_code == 403)

# channel_id and u_id are invalid
def test_invalid_u_id_and_channel_id(initial_data):
    user1_token = initial_data["user1_token"]
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": user1_token, "channel_id": 7774, "u_id": 775})
    assert(resp.status_code == 400)
    resp2 = requests.get(config.url + 'channel/invite/v2', params={"token": user1_token, "channel_id": 243, "u_id": 763})
    assert(resp2.status_code == 400)  

# token and u_id are invalid
def test_invalid_token_and_u_id(initial_data):
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": 776, "channel_id": public_channel_id, "u_id": 715})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/invite/v2', params={"token": 432, "channel_id": public_channel_id, "u_id": 352})
    assert(resp2.status_code == 403)

# token and channel_id are invalid
def test_invalid_token_and_channel_id(initial_data):
    user2_id = initial_data["user2_id"]
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": 7767, "channel_id": 5444, "u_id": user2_id})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/invite/v2', params={"token": 432, "channel_id": 243, "u_id": user2_id})
    assert(resp2.status_code == 403)

# All inputs are invalid
def test_invalid_inputs(initial_data):
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": 7767, "channel_id": 5444, "u_id": 6111})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/invite/v2', params={"token": 4321, "channel_id": 2431, "u_id": 3214})
    assert(resp2.status_code == 403)    

# user is already a member of the public channel.
def test_member_duplicate(initial_data):
    user1_token = initial_data["user1_token"]
    user2_id = initial_data["user2_id"]
    user2_token = initial_data["user2_token"]
    public_channel_id = initial_data["public_channel_id"]

    requests.post(config.url + 'channel/join/v2', json={"token": user2_token, "channel_id": public_channel_id})
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": user1_token, "channel_id": public_channel_id, "u_id": user2_id})
    assert(resp.status_code == 400)

# auth_user (invitee) is not a member of the public channel.
def test_invalid_invitee(initial_data):
    user3_id = initial_data["user3_id"]
    user2_token = initial_data["user2_token"]
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.get(config.url + 'channel/invite/v2', params={"token": user2_token, "channel_id": public_channel_id, "u_id": user3_id})
    assert(resp.status_code == 403)

# Arguments are valid.
# User is not a member of the channel.
# Invitee is a member of the channel.

# test user invited to public channel
def test_can_invite_public(initial_data):
    user1_token = initial_data["user1_token"]
    user2_token = initial_data["user2_token"] 
    user2_id = initial_data["user2_id"] 
    user3_id = initial_data["user3_id"]  
    public_channel_id = initial_data["public_channel_id"]

    requests.post(config.url + 'channel/invite/v2', json={"token": user1_token, "channel_id": public_channel_id, "token": user2_id})
    requests.post(config.url + 'channel/invite/v2', json={"token": user2_token, "channel_id": public_channel_id, "token": user3_id})
    
    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": public_channel_id})
    details = json.loads(details_response.text)
    assert(details["is_public"] == True)
    assert(details["name"] == "Rainbow Six Siege")
    members_list = details["all_members"]
    assert(len(members_list) == 3)
    owners_list = details["owner_members"]
    assert(len(owners_list) == 1)

# test user invited to private channel
def test_can_invite_private(initial_data):
    user1_token = initial_data["user1_token"]
    user2_token = initial_data["user2_token"]
    user2_id = initial_data["user2_id"] 
    user3_id = initial_data["user3_id"]
    private_channel_id = initial_data["private_channel_id"]

    requests.post(config.url + 'channel/invite/v2', json={"token": user1_token, "channel_id": private_channel_id, "token": user2_id})
    requests.post(config.url + 'channel/invite/v2', json={"token": user2_token, "channel_id": private_channel_id, "token": user3_id})   

    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": private_channel_id})
    details = json.loads(details_response.text)
    assert(details["name"] == "Minecraft")
    assert(details["is_public"] == False)
    members_list = details["all_members"]
    assert(len(members_list) == 3)
    owners_list = details["owner_members"]
    assert(len(owners_list) == 1)