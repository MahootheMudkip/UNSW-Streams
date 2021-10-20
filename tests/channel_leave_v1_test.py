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
    user3_token = user3["token"]
    user3_id = user3["auth_user_id"]
    # Register fourth user
    user4_response = requests.post(config.url + 'auth/register/v2', json={
        "email": "kelly.slater@gmail.com", 
        "password": "27012003", 
        "name_first": "Kelly", 
        "name_last": "Slater"
    })
    user4 = json.loads(user4_response.text)
    user4_token = user4["token"]
    # Make public channel
    public_channel_response = requests.post(config.url + 'channels/create/v2', json={
        "token": user1_token,
        "name": "Rainbow Six Siege",
        "is_public": True
    })
    public_channel = json.loads(public_channel_response.text)
    public_channel_id = public_channel["channel_id"]
    
    # Make users join the public channel
    # requests.post(config.url + 'channel/join/v2', json={
    #     "token": user2_token,
    #     "channel_id": public_channel_id
    # })
    # requests.post(config.url + 'channel/join/v2', json={
    #     "token": user3_token,
    #     "channel_id": public_channel_id
    # })

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
    values = {
        "user1_token": user1_token,
        "user2_token": user2_token,
        "user3_token": user3_token,
        "user4_token": user4_token,
        "public_channel_id": public_channel_id,
        "private_channel_id": private_channel_id
    }
    return values

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

def test_invalid_channel(initial_data):
    user1_token = initial_data["user1_token"]
    resp = requests.post(config.url + 'channel/leave/v1', json={"token": user1_token, "channel_id": 3332})
    assert(resp.status_code == INPUT_ERROR)

# the authorised user is not a member of the public channel
def test_auth_user_not_in_public_channel(initial_data):
    user2_token = initial_data["user2_token"]
    user3_token = initial_data["user3_token"]
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.post(config.url + 'channel/leave/v1', json={"token": user2_token, "channel_id": public_channel_id})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/leave/v1', json={"token": user3_token, "channel_id": public_channel_id})
    assert(resp2.status_code == ACCESS_ERROR)

# the authorised user is not a member of the private channel
def test_auth_user_not_in_private_channel(initial_data):
    user4_token = initial_data["user4_token"]
    private_channel_id = initial_data["private_channel_id"]
    resp = requests.post(config.url + 'channel/leave/v1', json={"token": user4_token, "channel_id": private_channel_id})
    assert(resp.status_code == ACCESS_ERROR)


# test user is invalid and public channel is valid
def test_user_invalid_and_public_channel_valid(initial_data):
    public_channel_id = initial_data["public_channel_id"]
    resp = requests.post(config.url + 'channel/leave/v1', json={"token": 4345, "channel_id": public_channel_id})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/leave/v1', json={"token": 1521, "channel_id": public_channel_id})
    assert(resp2.status_code == ACCESS_ERROR)

# test user is invalid and private channel is valid
def test_user_invalid_and_private_channel_valid(initial_data):
    private_channel_id = initial_data["private_channel_id"]
    resp = requests.post(config.url + 'channel/leave/v1', json={"token": 4345, "channel_id": private_channel_id})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/leave/v1', json={"token": 1531, "channel_id": private_channel_id})
    assert(resp2.status_code == ACCESS_ERROR)

# the authorised user is not a member of the channel and channel_id is invalid
def test_user_not_in_channel_and_invalid_channel_id(initial_data):
    user2_token = initial_data["user2_token"]
    resp = requests.post(config.url + 'channel/leave/v1', json={"token": user2_token, "channel_id": 5647})
    assert(resp.status_code == INPUT_ERROR)
    resp2 = requests.post(config.url + 'channel/leave/v1', json={"token": user2_token, "channel_id": 3231})
    assert(resp2.status_code == INPUT_ERROR)

# the authorised user is invalid and channel_id is invalid
def test_invalid_user_and_channel_id(initial_data):
    resp = requests.post(config.url + 'channel/leave/v1', json={"token": 4332, "channel_id": 1521})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.post(config.url + 'channel/leave/v1', json={"token": 1542, "channel_id": 5551})
    assert(resp2.status_code == ACCESS_ERROR)

# test leaving public channel
# def test_channel_leave_removes_user_public_channel(initial_data):
#     user1_token = initial_data["user1_token"]
#     user2_token = initial_data["user2_token"]
#     user3_token = initial_data["user3_token"]
#     public_channel_id = initial_data["public_channel_id"]
# 
#     requests.post(config.url + 'channel/leave/v1', json={
#         "token": user2_token,
#         "channel_id": public_channel_id
#         })
#     requests.post(config.url + 'channel/leave/v1', json={
#         "token": user3_token,
#         "channel_id": public_channel_id
#         })
# 
#     details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": public_channel_id})
#     details = json.loads(details_response.text)
# 
#     assert(details["is_public"] == True)
#     assert(details["name"] == "Rainbow Six Siege")
#     members_list = details["all_members"] 
#     assert(len(members_list) == 1)
#     owner_members_list = details["owner_members"]
#     assert(len(owner_members_list) == 1)

# testing users can leave private channel
def test_channel_leave_removes_user_private_channel(initial_data):
    user1_token = initial_data["user1_token"]
    user2_token = initial_data["user2_token"]
    user3_token = initial_data["user3_token"]
    private_channel_id = initial_data["private_channel_id"]

    leave_response0 = requests.post(config.url + 'channel/leave/v1', json={
        "token": user2_token,
        "channel_id": private_channel_id
        })
    assert(leave_response0.status_code == NO_ERROR)

    leave_response1 = requests.post(config.url + 'channel/leave/v1', json={
        "token": user3_token,
        "channel_id": private_channel_id
        })
    assert(leave_response1.status_code == NO_ERROR)

    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user1_token, "channel_id": private_channel_id})
    assert(details_response.status_code == NO_ERROR)
    details = json.loads(details_response.text)
    
    assert(details["is_public"] == False)
    assert(details["name"] == "Minecraft")
    members_list = details["all_members"] 
    assert(len(members_list) == 1)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 1)

# test owner can leave the channel
def test_channel_leave_removes_owner(initial_data):
    user1_token = initial_data["user1_token"]
    user2_token = initial_data["user2_token"]
    user3_token = initial_data["user3_token"]
    private_channel_id = initial_data["private_channel_id"]

    leave_response0 = requests.post(config.url + 'channel/leave/v1', json={
        "token": user1_token,
        "channel_id": private_channel_id
        })
    assert(leave_response0.status_code == NO_ERROR)

    leave_response1 = requests.post(config.url + 'channel/leave/v1', json={
        "token": user3_token,
        "channel_id": private_channel_id
        })
    assert(leave_response1.status_code == NO_ERROR)

    details_response = requests.get(config.url + 'channel/details/v2', params={"token": user2_token, "channel_id": private_channel_id})
    assert(details_response.status_code == NO_ERROR)
    details = json.loads(details_response.text)
    
    assert(details["is_public"] == False)
    assert(details["name"] == "Minecraft")
    members_list = details["all_members"] 
    assert(len(members_list) == 1)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 0)