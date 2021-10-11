import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1

@pytest.fixture
def initial_data():
    # clear used data
    clear_v1()
    # Register first user
    user1 = auth_register_v1("daniel.ricc@gmail.com", "27012003", "Daniel", "Ricciardo")
    user1_token = user1["token"]
    # Register second user
    user2 = auth_register_v1("lando.norris@gmail.com", "27012003", "Lando", "Norris")
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    # Register third user
    user3 = auth_register_v1("mick.fanning@gmail.com", "27012003", "Mick", "Fanning")
    user3_id = user3["auth_user_id"]
    user3_token = user3["token"]
    # Make public channel
    public_channel = channels_create_v1(user1_token, "Rainbow Six Siege", True)
    public_channel_id = public_channel["channel_id"]
    # Make private channel
    private_channel = channels_create_v1(user1_token, "Minecraft", False)
    private_channel_id = private_channel["channel_id"]
    
    values = {
        "user1_token": user1_token,
        "user2_token": user2_token,
        "user2_id": user2_id,
        "user3_token": user3_token,
        "user3_id": user3_id,
        "public_channel_id": public_channel_id,
        "private_channel_id": private_channel_id
    }
    return values

def test_invalid_channel(initial_data):
    user1_token = initial_data["user1_token"]
    resp = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": 3332})
    assert(resp.status_code == 400)

# the authorised user is not a member of the public channel
def test_auth_user_not_in_public_channel(initial_data):
    user2_token = initial_data["user2_token"]
    user3_token = initial_data["user3_token"]
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.get(config.url + 'channel/details/v2', params={"token": user2_token, "channel_id": public_channel_id})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/details/v2', params={"token": user3_token, "channel_id": public_channel_id})
    assert(resp2.status_code == 403)

# the authorised user is not a member of the private channel
def test_auth_user_not_in_private_channel(initial_data):
    user2_token = initial_data["user2_token"]
    user3_token = initial_data["user3_token"]
    private_channel_id = initial_data["private_channel_id"]
    resp = requests.get(config.url + 'channel/details/v2', params={"token": user2_token, "channel_id": private_channel_id})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/details/v2', params={"token": user3_token, "channel_id": private_channel_id})
    assert(resp2.status_code == 403)

# test user is invalid and public channel is valid
def test_user_invalid_and_public_channel_valid(initial_data):
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.get(config.url + 'channel/details/v2', params={"token": 4345, "channel_id": public_channel_id})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/details/v2', params={"token": 1521, "channel_id": public_channel_id})
    assert(resp2.status_code == 403)

# test user is invalid and private channel is valid
def test_user_invalid_and_private_channel_valid(initial_data):
    private_channel_id = initial_data["private_channel_id"]
    resp = requests.get(config.url + 'channel/details/v2', params={"token": 4345, "channel_id": private_channel_id})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/details/v2', params={"token": 1531, "channel_id": private_channel_id})
    assert(resp2.status_code == 403)

# the authorised user is not a member of the channel and channel_id is invalid
def test_user_not_in_channel_and_invalid_channel_id(initial_data):
    user2_token = initial_data["user2_token"]
    resp = requests.get(config.url + 'channel/details/v2', params={"token": user2_token, "channel_id": 5647})
    assert(resp.status_code == 400)
    resp2 = requests.get(config.url + 'channel/details/v2', params={"token": user2_token, "channel_id": 3231})
    assert(resp2.status_code == 400)

# the authorised user is invalid and channel_id is invalid
def test_invalid_user_and_channel_id(initial_data):
    resp = requests.get(config.url + 'channel/details/v2', params={"token": 4332, "channel_id": 1521})
    assert(resp.status_code == 403)
    resp2 = requests.get(config.url + 'channel/details/v2', params={"token": 1542, "channel_id": 5551})
    assert(resp2.status_code == 403)

# testing showing details of public channel
def test_channel_details_v1_shows_public_channel_details(initial_data):
    user1_token = initial_data["user1_token"]
    user2_token = initial_data["user2_token"]
    user3_token = initial_data["user3_token"]
    public_channel_id = initial_data["public_channel_id"]
    requests.post(config.url + 'channel/join/v2', params={"token": user2_token, "channel_id": public_channel_id})
    requests.post(config.url + 'channel/join/v2', params={"token": user3_token, "channel_id": public_channel_id})
   
    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": public_channel_id})
    details = json.loads(details_response.text)
    
    assert(details["is_public"] == True)
    assert(details["name"] == "Rainbow Six Siege")
    members_list = details["all_members"] 
    assert(len(members_list) == 3)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 1)

# testing showing details of private channel
def test_channel_details_v1_shows_private_channel_details(initial_data):
    user1_token = initial_data["user1_token"]
    user2_token = initial_data["user2_token"]
    user2_id = initial_data["user2_id"]
    user3_id = initial_data["user3_id"]
    private_channel_id = initial_data["private_channel_id"]

    requests.post(config.url + 'channel/invite/v2', params={"token": user1_token, "channel_id": private_channel_id, "token": user2_id})
    requests.post(config.url + 'channel/invite/v2', params={"token": user2_token, "channel_id": private_channel_id, "token": user3_id})    
    
    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": private_channel_id})
    details = json.loads(details_response.text)

    assert(details["is_public"] == False)
    assert(details["name"] == "Minecraft")
    members_list = details["all_members"] 
    assert(len(members_list) == 3)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 1)
