import json
import pytest
import requests
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

URL = url + "admin/user/remove/v1"

@pytest.fixture
def initial_data():
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
    user1_id = user1["auth_user_id"]
    
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
        "email":        "richar@gmail.com", 
        "password":     "234789",
        "name_first":   "Richard",
        "name_last":    "Hammond"
    })
    user3 = user3_response.json()
    user3_id = user3["auth_user_id"]

    # create public channel and extract channel_id
    public_channel_response = requests.post(channel_create_url, json={
        "token":        user2_token,
        "name":         "public_channel",
        "is_public":    True
    })
    public_channel = public_channel_response.json()
    public_channel_id = public_channel["channel_id"]

    # Make user0 join the public channel
    requests.post(url + 'channel/join/v2', json={
        "token": user0_token,
        "channel_id": public_channel_id
    })

    # create public channel and extract channel_id
    public_channel_response = requests.post(channel_create_url, json={
        "token":        user0_token,
        "name":         "channel",
        "is_public":    True
    })
    public_channel = public_channel_response.json()
    channel_id = public_channel["channel_id"]

    # create private channel and extract channel_id
    private_channel_response = requests.post(channel_create_url, json={
        "token":        user0_token,
        "name":         "public_channel",
        "is_public":    False
    })
    private_channel = private_channel_response.json()
    private_channel_id = private_channel["channel_id"]

    # Invite user2 to private channel
    requests.post(url + 'channel/invite/v2', json={
        "token": user0_token,
        "channel_id": private_channel_id,
        "u_id": user2_id
    })

    # create dms
    response = requests.post(url + "dm/create/v1", json={"token":user0_token,"u_ids":[user1_id,user2_id]})
    assert response.status_code == NO_ERROR
    dm1_id = response.json()["dm_id"]

    response = requests.post(url + "dm/create/v1", json={"token":user2_token,"u_ids":[user1_id, user3_id]})
    assert response.status_code == NO_ERROR
    dm2_id = response.json()["dm_id"]

    response = requests.post(url + "dm/create/v1", json={"token":user0_token,"u_ids":[user1_id, user3_id]})
    assert response.status_code == NO_ERROR

    message_id_public = []
    message_id_private = []

    # create messages in public and private channels
    for i in range(3):
        response = requests.post(f"{url}message/send/v1", json={
            "token":        user2_token,
            "channel_id":   public_channel_id,
            "message":      f"Hello there! I am message {i}!"
        })
        assert response.status_code == NO_ERROR
        data = response.json()
        message_id_public.append(data["message_id"])
    
    for j in range(3):
        response = requests.post(f"{url}message/send/v1", json={
            "token":        user2_token,
            "channel_id":   private_channel_id,
            "message":      f"Bye! I am message {j}!"
        })
        assert response.status_code == NO_ERROR
        data = response.json()
        message_id_private.append(data["message_id"])
    
    for k in range(3):
        response = requests.post(f"{url}message/send/v1", json={
            "token":        user0_token,
            "channel_id":   channel_id,
            "message":      f"Bye! I am message {k}!"
        })
        assert response.status_code == NO_ERROR
        data = response.json()
        message_id_private.append(data["message_id"])

    # create messages in dms
#    for i in range(3):
#        response = requests.post(f"{url}message/senddm/v1", json={
#            "token":        user2_token,
#            "channel_id":   dm1_id,
#            "message":      f"Hello there! I am message {i}!"
#        })
#        assert response.status_code == NO_ERROR
#        data = response.json()
#        message_id_public.append(data["message_id"])
#
#    for j in range(3):
#        response = requests.post(f"{url}message/senddm/v1", json={
#            "token":        user2_token,
#            "channel_id":   dm2_id,
#            "message":      f"Bye! I am message {i}!"
#        })
#        assert response.status_code == NO_ERROR
#        data = response.json()
#        message_id_public.append(data["message_id"])

    return {
        "user0_token":          user0_token,
        "user0_id":             user0_id,
        "user1_token":          user1_token,
        "user1_id":             user1_id,
        "user2_token":          user2_token,
        "user2_id":             user2_id,
        "message_id_public":    message_id_public,
        "message_id_private":   message_id_private,
        "public_channel_id":    public_channel_id,
        "private_channel_id":   private_channel_id,
        "dm1_id":               dm1_id,
        "dm2_id":               dm2_id
    }



# u_id does not refer to a valid user. token is valid.
def test_invalid_u_id_only(initial_data):
    user0_token = initial_data["user0_token"]
    resp = requests.delete(URL, json={"token": user0_token, "u_id": 7775})
    assert(resp.status_code == INPUT_ERROR)  

# token does not refer to a valid user. u_id is valid
def test_invalid_token_only(initial_data):
    user2_id = initial_data["user2_id"]
    resp = requests.delete(URL, json={"token": 7773, "u_id": user2_id})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.delete(URL, json={"token": 532, "u_id": user2_id})
    assert(resp2.status_code == ACCESS_ERROR)

# All inputs are invalid
def test_invalid_inputs(initial_data):
    resp = requests.delete(URL, json={"token": 7767, "u_id": 6111})
    assert(resp.status_code == ACCESS_ERROR)
    resp2 = requests.delete(URL, json={"token": 4321, "u_id": 3214})
    assert(resp2.status_code == ACCESS_ERROR)

# u_id is the only global owner.
def test_u_id_only_global_owner(initial_data):
    user0_token = initial_data["user0_token"]
    user0_id = initial_data["user0_id"]
    resp = requests.delete(URL, json={"token": user0_token, "u_id": user0_id})
    assert(resp.status_code == INPUT_ERROR)

# The authorised user is not a global owner
def test_auth_user_not_global_owner(initial_data):
    user2_token = initial_data["user2_token"]
    user1_id = initial_data["user1_id"]

    resp = requests.delete(URL, json={"token": user2_token, "u_id": user1_id})
    assert(resp.status_code == ACCESS_ERROR)

# remove user2
def test_admin_user_remove_user2(initial_data):
    user0_token = initial_data["user0_token"]
    user2_token = initial_data["user2_token"]
    user2_id = initial_data["user2_id"]
    public_channel_id = initial_data["public_channel_id"]
    private_channel_id = initial_data["private_channel_id"]
#    dm1_id = initial_data["dm1_id"]
#    dm2_id = initial_data["dm2_id"]
    user_profile_response = requests.get(url + 'user/profile/v1', params={"token": user2_token, "u_id": user2_id})
    assert(user_profile_response.status_code == NO_ERROR)
    user_response = user_profile_response.json()
    user = user_response["user"]
    reusable_handle = user["handle_str"]
    reusable_email = user["email"]

    # remove user
    resp = requests.delete(URL, json={"token": user0_token, "u_id": user2_id})
    assert(resp.status_code == NO_ERROR)

    # check user has been removed from channels
    details_response = requests.get(url + 'channel/details/v2', params={"token": user0_token, "channel_id": public_channel_id})
    assert(details_response.status_code == NO_ERROR)
    details = json.loads(details_response.text)

    members_list = details["all_members"] 
    assert(len(members_list) == 1)

    details_response = requests.get(url + 'channel/details/v2', params={"token": user0_token, "channel_id": private_channel_id})
    assert(details_response.status_code == NO_ERROR)
    details = json.loads(details_response.text)

    members_list = details["all_members"] 
    assert(len(members_list) == 1)

    # check user has been removed from dms
#    details_response = requests.get(url + 'dm/details/v1', params={"token": user0_token, "channel_id": dm1_id})
#    assert(details_response.status_code == NO_ERROR)
#    details = json.loads(details_response.text)
#
#    members_list = details["members"] 
#    assert(len(members_list) == 1)
#
#    details_response = requests.get(url + 'dm/details/v1', params={"token": user0_token, "channel_id": dm2_id})
#    assert(details_response.status_code == NO_ERROR)
#    details = json.loads(details_response.text)
#
#    members_list = details["members"] 
#    assert(len(members_list) == 2)

    # check channel messages have been replaced with 'Removed user'
    channel_messages_response = requests.get(url + 'channel/messages/v2', params={"token": user0_token, "channel_id": public_channel_id, "start": 0})
    assert(channel_messages_response.status_code == NO_ERROR)
    details = json.loads(channel_messages_response.text)

    messages = details["messages"]
    assert messages[0]["message"] == "Removed user"
    assert messages[1]["message"] == "Removed user"
    assert messages[2]["message"] == "Removed user"

    channel_messages_response = requests.get(url + 'channel/messages/v2', params={"token": user0_token, "channel_id": private_channel_id, "start": 0})
    assert(channel_messages_response.status_code == NO_ERROR)
    details = json.loads(channel_messages_response.text)

    messages = details["messages"]
    assert messages[0]["message"] == "Removed user"
    assert messages[1]["message"] == "Removed user"
    assert messages[2]["message"] == "Removed user"

    # check dm messages have been replaced with 'Removed user'
#    dm_messages_response = requests.get(url + 'dm/messages/v1', params={"token": user0_token, "dm_id": dm1_id, "start": 0})
#    assert(dm_messages_response.status_code == NO_ERROR)
#    details = json.loads(dm_messages_response.text)
#
#    messages = details["messages"]
#    messages[0]["message"] = "Removed user"
#    messages[1]["message"] = "Removed user"
#    messages[2]["message"] = "Removed user"
#    messages[3]["message"] = "Removed user"
#
#    dm_messages_response = requests.get(url + 'channel/messages/v2', params={"token": user0_token, "dm_id": dm2_id, "start": 0})
#    assert(dm_messages_response.status_code == NO_ERROR)
#    details = json.loads(dm_messages_response.text)
#
#    messages = details["messages"]
#    messages[0]["message"] = "Removed user"
#    messages[1]["message"] = "Removed user"
#    messages[2]["message"] = "Removed user"
#    messages[3]["message"] = "Removed user"

    # check name_first is 'Removed' and name_last is 'user'
    user_profile_response = requests.get(url + 'user/profile/v1', params={"token": user0_token, "u_id": user2_id})
    assert(user_profile_response.status_code == NO_ERROR)
    user_response = user_profile_response.json()
    user = user_response["user"]

    assert user["name_first"] == "Removed"
    assert user["name_last"] == "user"

    # check handle_str and email are reusable
    new_user_response = requests.post(url + 'auth/register/v2', json={      
        "email":        "wtf@gmail.com", 
        "password":     "234789",
        "name_first":   "James",
        "name_last":    "May"
    })
    assert(new_user_response.status_code == NO_ERROR)
    new_user = new_user_response.json()
    token = new_user["token"]
    u_id = new_user["auth_user_id"]

    user_profile_response = requests.get(url + 'user/profile/v1', params={"token": token, "u_id": u_id})
    assert(user_profile_response.status_code == NO_ERROR)
    new_user_profile_response = json.loads(user_profile_response.text)

    new_user = new_user_profile_response["user"]
    assert(new_user["handle_str"] == reusable_handle)
    assert(new_user["email"] == reusable_email)