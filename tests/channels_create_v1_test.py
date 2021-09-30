import pytest 

from src.auth import auth_register_v1
from src.other import clear_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.channel import channel_details_v1

@pytest.fixture
def data(): 
    clear_v1()
    #create a User
    user1 =  auth_register_v1("dead@inside.com", "5343q46", "Pablo", "Escobar")
    id1 = user1["auth_user_id"]
    #create a User
    user2 =  auth_register_v1("Ineed@sleep.com", "4zxcv43", "sponge", "bob")
    id2 = user2["auth_user_id"]

    values = {
        "id2" : id2,
        "id1" : id1
    }
    return values

#testing when the user is invalid and a valid name
def test_channels_create_v1_invalid_user_and_valid_name(data):
    with pytest.raises(AccessError):
        channels_create_v1(-2543, "Mr. Krabs", True)
    with pytest.raises(AccessError):
        channels_create_v1(-1, "Channel1", False)

#testing when the user is invalid and invalid name 
def test_channels_create_v1_invalid_user_and_invalid_name(data):
    #less than one character
    with pytest.raises(AccessError):
        channels_create_v1(-2543, "", True)
    #greater than 20 character
    with pytest.raises(AccessError):
        channels_create_v1(-2543, "abcdefghijklmnopqrstuvwxyz", False)

#testing when the user is valid with a invalid name 
def test_channels_create_v1_valid_user_and_invalid_name(data):
    #less than one character
    id1 = data["id1"]
    id2 = data["id2"]
    with pytest.raises(InputError):
        channels_create_v1(id2, "", False)
    #greater than 20 character
    with pytest.raises(InputError):
        channels_create_v1(id1, "abcdefghijklmnopqrstuvwxyz", True)

# #testing when the user is valid with a valid name 
# def test_channels_create_v1_valid_parameters(data):
#     id1 = data["id1"]
#     id2 = data["id2"]

#     channel1_id = channels_create_v1(id1, "Channel1", True)
#     channel_info1 = channel_details_v1(id1, channel1_id)
#     assert (channel_info1["name"] == "Channel1")
#     assert (channel_info1["is_public"] == True)
#     assert (len(channel_info1["owner_members"]) == 1)
#     assert (len(channel_info1["all_members"]) == 1)

#     channel2_id = channels_create_v1(id2, "Channel2", False)
#     channel_info2 = channel_details_v1(id2, channel2_id)
#     assert (channel_info2["name"] == "Channel2")
#     assert (channel_info2["is_public"] == False)
#     assert (len(channel_info2["owner_members"]) == 1)
#     assert (len(channel_info2["all_members"]) == 1)
