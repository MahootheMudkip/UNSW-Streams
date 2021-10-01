import pytest

from src.channel import channel_join_v1, channel_details_v1, channel_invite_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1

@pytest.fixture
def initial_setup():
    # clear stored data
    clear_v1() 
    # make new user1
    user1 = auth_register_v1("lmao@gmail.com", "123789", "Jeremy", "Clarkson")
    user1_id = user1["auth_user_id"]
    # make new user2
    user2 = auth_register_v1("wtf@gmail.com", "234789", "James", "May")
    user2_id = user2["auth_user_id"]
    # make new user3
    user3 = auth_register_v1("pwd@gmail.com", "456789", "Richard", "Hammond")
    user3_id = user3["auth_user_id"]
    # make 4 new channels
    channel_1 = channels_create_v1(user1_id, "channel_1", True)
    channel_1_id = channel_1["channel_id"]
    channel_2 = channels_create_v1(user1_id, "channel_2", True)
    channel_2_id = channel_2["channel_id"]
    channel_3 = channels_create_v1(user1_id, "channel_3", False)
    channel_3_id = channel_3["channel_id"]
    channel_4 = channels_create_v1(user1_id, "channel_4", False)
    channel_4_id = channel_4["channel_id"]
    values = {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "user3_id": user3_id,
        "channel_1_id": channel_1_id,
        "channel_2_id": channel_2_id,
        "channel_3_id": channel_3_id,
        "channel_4_id": channel_4_id,
    }
    return values

# testing invalid channel
def test_channel_join_v1_except_InputError_invalid_channel(initial_setup):
    user1_id = initial_setup["user1_id"]
    with pytest.raises(InputError):
        channel_join_v1(user1_id, -345)
    with pytest.raises(InputError):
        channel_join_v1(user1_id, -4242)

# testing private channel and user not already in channel
def test_channel_join_v1_except_AccessError_unauthorised_user(initial_setup):
    user2_id = initial_setup["user2_id"]
    user3_id = initial_setup["user3_id"]   
    channel_3_id = initial_setup["channel_3_id"]
    channel_4_id = initial_setup["channel_4_id"]
    with pytest.raises(AccessError):
        channel_join_v1(user2_id, channel_3_id)
    with pytest.raises(AccessError):
        channel_join_v1(user3_id, channel_4_id)

# testing user (owner) already in public channel
def test_channel_join_v1_except_InputError_already_in_public_channel_owner(initial_setup):
    user1_id = initial_setup["user1_id"]    
    channel_1_id = initial_setup["channel_1_id"]
    with pytest.raises(InputError):
        channel_join_v1(user1_id, channel_1_id)

# testing user (owner) already in private channel
def test_channel_join_v1_except_InputError_already_in_private_channel_owner(initial_setup):
    user1_id = initial_setup["user1_id"]    
    channel_3_id = initial_setup["channel_3_id"]
    with pytest.raises(InputError):
        channel_join_v1(user1_id, channel_3_id)        

# testing user already in public channel
def test_channel_join_v1_except_InputError_already_in_public_channel(initial_setup):
    user3_id = initial_setup["user3_id"]    
    channel_1_id = initial_setup["channel_1_id"]
    channel_join_v1(user3_id, channel_1_id)
    with pytest.raises(InputError):
        channel_join_v1(user3_id, channel_1_id)  

# # testing user already in private channel
# def test_channel_join_v1_except_InputError_already_in_private_channel(initial_setup):
#     user3_id = initial_setup["user3_id"]    
#     channel_3_id = initial_setup["channel_3_id"]
#     user1_id = initial_setup["user1_id"]
#     channel_invite_v1(user1_id, channel_3_id, user3_id)
#     with pytest.raises(InputError):
#         channel_join_v1(user3_id, channel_3_id)  

# # testing adding user to public channel
# def test_channel_join_v1_adding_user(initial_setup):
#     user3_id = initial_setup["user3_id"]    
#     channel_1_id = initial_setup["channel_1_id"]
#     user2_id = initial_setup["user2_id"]    

#     channel_join_v1(user3_id, channel_1_id)
#     details = channel_details_v1(user3_id, channel_1_id)
#     assert(details["is_public"] == True)
#     assert(details["name"] == "channel_1") 
#     members = details["all_members"]
#     assert(len(members) == 2)  

#     details2 = channel_join_v1(user2_id, channel_1_id)
#     members2 = details2["all_members"]
#     assert(len(members2) == 3)

# user does not exist, valid channel
def test_channel_join_v1_user_does_not_exist(initial_setup):
    channel_1_id = initial_setup["channel_1_id"]
    with pytest.raises(AccessError):
        channel_join_v1(99999999999342, channel_1_id)

# user does not exist, invalid channel
def test_channel_join_v1_user_and_channel_does_not_exist(initial_setup):
    with pytest.raises(AccessError):
        channel_join_v1(99999999999342, 9283492834)

# # user is in a private channel, but is not an owner
# def test_channel_join_v1_user_in_private_channel_and_not_owner(initial_setup):
#     channel_4_id = initial_setup["channel_4_id"]
#     user1_id = initial_setup["user1_id"]
#     user2_id = initial_setup["user2_id"]
#     channel_invite_v1(user1_id, channel_4_id, user2_id)
#     # user1 invites user2 to channel 4 (which is private)
#     with pytest.raises(InputError):
#         channel_join_v1(user2_id, channel_4_id) 
