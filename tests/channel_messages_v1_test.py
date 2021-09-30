import pytest

from src.channel import channel_messages_v1
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
    values = {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "user3_id": user3_id,
        "channel_1_id": channel_1_id,
        "channel_2_id": channel_2_id,
        "channel_3_id": channel_3_id,
    }
    return values

# testing valid user, but non-existent channel
def test_channel_messages_v1_except_InputError_invalid_channel(initial_setup):
    user1_id = initial_setup["user1_id"]
    with pytest.raises(InputError):
        channel_messages_v1(user1_id, -2343847837, 0)

# testing non-existent user, but valid public channel
def test_channel_messages_v1_except_AccessError_non_existent_user(initial_setup):
    channel_1_id = initial_setup["channel_1_id"]
    with pytest.raises(AccessError):
        channel_messages_v1(-23423, channel_1_id, 0)

# testing non-existent user, but valid private channel
def test_channel_messages_v1_except_AccessError_non_existent_user(initial_setup):
    channel_3_id = initial_setup["channel_3_id"]
    with pytest.raises(AccessError):
        channel_messages_v1(-23423, channel_3_id, 0)

# user and channel exists, but user is not part of channel
def test_channel_messages_v1_except_AccessError_unauthorised_user(initial_setup):
    channel_2_id = initial_setup["channel_2_id"]
    user3_id = initial_setup["user3_id"]
    with pytest.raises(AccessError):
        channel_messages_v1(user3_id, channel_2_id, 0)

# channel id is invalid and user does not exist
def test_channel_messages_v1_except_AccessError_non_existent_user_and_channel(initial_setup):
    with pytest.raises(AccessError):
        channel_messages_v1(-3423434, -2342343434, 0)

# channel id is invalid and user exists, but not part of channel
def test_channel_messages_v1_except_InputError_non_existent_channel_and_unauthorised_user(initial_setup):
    user1_id = initial_setup["user1_id"]
    with pytest.raises(InputError):
        channel_messages_v1(user1_id, -2342584587, 0)

# test all valid except start
def test_channel_messages_v1_except_InputError_invalid_start(initial_setup):
    user1_id = initial_setup["user1_id"]
    channel_1_id = initial_setup["channel_1_id"]
    with pytest.raises(InputError):
        channel_messages_v1(user1_id, channel_1_id, 4)
    with pytest.raises(InputError):
        channel_messages_v1(user1_id, channel_1_id, -23434)

# test return values, all valid parameters
def test_channel_messages_v1_all_valid(initial_setup):
    user1_id = initial_setup["user1_id"]
    channel_1_id = initial_setup["channel_1_id"]
    message_values = channel_messages_v1(user1_id, channel_1_id, 0)
    assert (len(message_values["messages"]) == 0)
    assert (message_values["start"] == 0)
    assert (message_values["end"] == -1) 

