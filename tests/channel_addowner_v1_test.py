import pytest
import requests
import json

from src import config

# fixture for registering and logging in user to avoid repetition.
@pytest.fixture
def initial_data():
    # clear used data
    requests.delete(config.url + 'clear/v1')
    # Register first user
    user1_response = requests.post(config.url + 'auth/register/v2', json={
        "email": "daniel.ricc@gmail.com", 
        "password": "27012003", 
        "name_first": "Daniel", 
        "name_last": "Ricciardo"
    })
    user1 = json.loads(user1_response.text)
    user1_token = user1["token"]
    # Register second user
    user2_response = requests.post(config.url + 'auth/register/v2', json={
        "email": "lando.norris@gmail.com", 
        "password": "27012003", 
        "name_first": "Lando", 
        "name_last": "Norris"
    })
    user2 = json.loads(user2_response.text)
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]
    # Register third user
    user3_response = requests.post(config.url + 'auth/register/v2', json={
        "email": "mick.fanning@gmail.com", 
        "password": "27012003", 
        "name_first": "Mick", 
        "name_last": "Fanning"
    })
    user3 = json.loads(user3_response.text)
    user3_id = user3["auth_user_id"]
    user3_token = user3["token"]
    # Make public channel
    public_channel_response = requests.post(config.url + 'channels/create/v2', json={
        "token": user1_token,
        "name": "Rainbow Six Siege",
        "is_public": True
    })
    public_channel = json.loads(public_channel_response.text)
    public_channel_id = public_channel["channel_id"]
    # Make users join the public channel
    requests.post(config.url + 'channel/join/v2', json={
        "token": user2_token,
        "channel_id": public_channel_id
    })
    requests.post(config.url + 'channel/join/v2', json={
        "token": user3_token,
        "channel_id": public_channel_id
    })
    # Make private channel
    private_channel_response = requests.post(config.url + 'channels/create/v2', json={
        "token": user1_token,
        "name": "Minecraft",
        "is_public": False
    })
    private_channel = json.loads(private_channel_response.text)
    private_channel_id = private_channel["channel_id"]
    # Invite users to private channel
    requests.post(config.url + 'channel/invite/v2', json={
        "token": user1_token,
        "channel_id": private_channel_id,
        "u_id": user2_id
    })
    requests.post(config.url + 'channel/invite/v2', json={
        "token": user1_token,
        "channel_id": private_channel_id,
        "u_id": user3_id
    })
    # Make channel created by user2
    channel0_response = requests.post(config.url + 'channels/create/v2', json={
        "token": user2_token,
        "name": "channel0",
        "is_public": True
    })
    channel0 = json.loads(channel0_response.text)
    channel0_id = channel0["channel_id"]
    # Join channel0 with global user
    requests.post(config.url + 'channel/invite/v2', json={
        "token": user1_token,
        "channel_id": channel0_id,
        "u_id": user2_id
    })
    
    values = {
        "user1_token": user1_token,
        "user2_token": user2_token,
        "user3_token": user3_token,
        "user2_id": user2_id,
        "user3_id": user3_id,
        "public_channel_id": public_channel_id,
        "private_channel_id": private_channel_id,
        "channel0_id": channel0_id
    }
    return values

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

# channel_id does not refer to a valid channel. token and u_id are both valid.
def test_invalid_channel_only(initial_data):
    user1_token = initial_data["user1_token"]
    user2_id = initial_data["user2_id"]
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user1_token, "channel_id": 1747, "u_id": user2_id})
    assert(resp.status_code == INPUT_ERROR)

# u_id does not refer to a valid user. token and channel_id are both valid.
def test_invalid_u_id_only(initial_data):
    user1_token = initial_data["user1_token"]
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user1_token, "channel_id": public_channel_id, "u_id": 7775})
    assert(resp.status_code == INPUT_ERROR)  

# token does not refer to a valid user. channel_id and u_id are both valid
def test_invalid_token_only(initial_data):
    user2_id = initial_data["user2_id"]
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": 7773, "channel_id": public_channel_id, "u_id": user2_id})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={"token": 532, "channel_id": public_channel_id, "u_id": user2_id})
    assert(resp2.status_code == ACCESS_ERROR)

# channel_id and u_id are invalid
def test_invalid_u_id_and_channel_id(initial_data):
    user1_token = initial_data["user1_token"]
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user1_token, "channel_id": 7774, "u_id": 775})
    assert(resp.status_code == INPUT_ERROR)
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={"token": user1_token, "channel_id": 243, "u_id": 763})
    assert(resp2.status_code == INPUT_ERROR)  

# token and u_id are invalid
def test_invalid_token_and_u_id(initial_data):
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": 776, "channel_id": public_channel_id, "u_id": 715})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={"token": 432, "channel_id": public_channel_id, "u_id": 352})
    assert(resp2.status_code == ACCESS_ERROR)

# token and channel_id are invalid
def test_invalid_token_and_channel_id(initial_data):
    user2_id = initial_data["user2_id"]
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": 7767, "channel_id": 5444, "u_id": user2_id})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={"token": 432, "channel_id": 243, "u_id": user2_id})
    assert(resp2.status_code == ACCESS_ERROR)

# All inputs are invalid
def test_invalid_inputs(initial_data):
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": 7767, "channel_id": 5444, "u_id": 6111})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={"token": 4321, "channel_id": 2431, "u_id": 3214})
    assert(resp2.status_code == ACCESS_ERROR)

# channel_id is valid but the authorised user does not have owner permissions in the channel
def test_auth_user_isnt_owner():
    user2_token = initial_data["user2_token"]
    user2_id = initial_data["user2_id"]
    user3_token = initial_data["user3_token"]
    user3_id = initial_data["user3_id"]
    public_channel_id = initial_data["public_channel_id"]

    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user2_token, "channel_id": public_channel_id, "u_id": user3_id})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={"token": user3_token, "channel_id": public_channel_id, "u_id": user2_id})
    assert(resp2.status_code == ACCESS_ERROR)

# u_id refers to a user who is already an owner of the channel
def test_u_id_is_an_owner(initial_data):
    user2_id = initial_data["user2_id"]
    user1_token = initial_data["user1_token"]
    channel0_id = initial_data["channel0_id"]
    
    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user1_token, "channel_id": channel0_id, "u_id": user2_id})
    assert(resp.status_code == INPUT_ERROR)


# test adds two owners to the private channel
def test_adding_owner_private_channel(initial_data):
    user1_token = initial_data["user1_token"]
    user2_id = initial_data["user2_id"]
    user2_token = initial_data["user2_token"]
    user3_id = initial_data["user3_id"]
    private_channel_id = initial_data["private_channel_id"]

    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user1_token, "channel_id": private_channel_id, "u_id": user2_id})
    assert(resp.status_code == NO_ERROR)

    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user2_token, "channel_id": private_channel_id, "u_id": user3_id})
    assert(resp.status_code == NO_ERROR)

    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": private_channel_id})
    assert(details_response.status_code == NO_ERROR)
    details = json.loads(details_response.text)
    
    assert(details["is_public"] == False)
    assert(details["name"] == "Minecraft")
    members_list = details["all_members"] 
    assert(len(members_list) == 3)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 3)

# test adds two owners to the public channel
    user1_token = initial_data["user1_token"]
    user2_id = initial_data["user2_id"]
    user2_token = initial_data["user2_token"]
    user3_id = initial_data["user3_id"]
    public_channel_id = initial_data["public_channel_id"]

    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user1_token, "channel_id": public_channel_id, "u_id": user2_id})
    assert(resp.status_code == NO_ERROR)

    resp = requests.post(config.url + 'channel/addowner/v1', json={"token": user2_token, "channel_id": public_channel_id, "u_id": user3_id})
    assert(resp.status_code == NO_ERROR)

    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": public_channel_id})
    assert(details_response.status_code == NO_ERROR)
    details = json.loads(details_response.text)
    
    assert(details["is_public"] == True)
    assert(details["name"] == "Rainbow Six Siege")
    members_list = details["all_members"] 
    assert(len(members_list) == 3)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 3)
