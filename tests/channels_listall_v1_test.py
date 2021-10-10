import pytest 

from src.auth import auth_register_v1
from src.other import clear_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.channels import channels_listall_v1

@pytest.fixture
def data(): 
    clear_v1()
    #create a User
    user1 =  auth_register_v1("dead@inside.com", "53vsfsfgg46", "Pablo", "Escobar")
    id1 = user1["auth_user_id"]
    #create a User
    user2 =  auth_register_v1("Ineed@sleep.com", "43fsdvsfr", "sponge", "bob")
    id2 = user2["auth_user_id"]

    # make 5 new channels
    channel1 = channels_create_v1(id1, "channel1", True)
    channel1_id = channel1["channel_id"]
    channel2 = channels_create_v1(id1, "channel2", False)
    channel2_id = channel2["channel_id"]
    channel3 = channels_create_v1(id1, "channel3", True)
    channel3_id = channel3["channel_id"]
    channel4 = channels_create_v1(id1, "channel4", False)
    channel4_id = channel4["channel_id"]
    channel5 = channels_create_v1(id1, "channel5", True)
    channel5_id = channel5["channel_id"]
    
    values = {
        "id1": id1,
        "id2": id2,
        "channel1_id": channel1_id,
        "channel2_id": channel2_id,
        "channel3_id": channel3_id,
        "channel4_id": channel4_id,
        "channel5_id": channel5_id,
    }
    return values


#testing invalid user id
def test_channels_listall_v1_invalid_user_id(data):
    with pytest.raises(AccessError):
        channels_listall_v1(-4625)

#testing the number of channels returned
def test_channels_listall_v1_num_channels_returned(data):
    id1 = data["id1"]
    id2 = data["id2"]
    
    assert (len(channels_listall_v1(id1)["channels"]) == 5)
    assert (len(channels_listall_v1(id2)["channels"]) == 5)

#if user 1 and user 2, both are registered users, both will return the same list on calling listall 
def test_channels_listall_v1_equal(data):
    id1 = data["id1"]
    id2 = data["id2"]

    list_of_channels_dict1 = channels_listall_v1(id1)["channels"]
    list_of_channels_dict2 = channels_listall_v1(id2)["channels"]

    assert (list_of_channels_dict1 == list_of_channels_dict2)

#testing if the right channel details have been returned
def test_channels_listall_v1_channels_returned(data):
    id1 = data["id1"]
    list_of_channels_dict1 = channels_listall_v1(id1)["channels"]
    
    assert list_of_channels_dict1[0]["name"] == "channel1"
    assert list_of_channels_dict1[0]["channel_id"] == data["channel1_id"]
   
    assert list_of_channels_dict1[1]["name"] == "channel2"
    assert list_of_channels_dict1[1]["channel_id"] == data["channel2_id"]
    
    assert list_of_channels_dict1[2]["name"] == "channel3"
    assert list_of_channels_dict1[2]["channel_id"] == data["channel3_id"]
    
    assert list_of_channels_dict1[3]["name"] == "channel4"
    assert list_of_channels_dict1[3]["channel_id"] == data["channel4_id"]
    
    assert list_of_channels_dict1[4]["name"] == "channel5"
    assert list_of_channels_dict1[4]["channel_id"] == data["channel5_id"]
    

