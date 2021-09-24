import pytest

from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1
from src.error import InputError
from src.error import AccessError

# fixture for registering and logging in user to avoid repetition.
@pytest.fixture
def initial_data():
    # clear used data
    clear_v1()
    # Register first user
    user1 = auth_register_v1("daniel.ricciardo@gmail.com", "27012003", "Daniel", "Ricciardo")
    user1_id = user1["auth_user_id"]
    # Register second user 
    user2 = auth_register_v1("lando.norris@gmail.com", "27012003", "Lando", "Norris")
    user2_id = user2["auth_user_id"]
    # Register third user
    user3 = auth_register_v1("mick.fanning@gmail.com", "27012003", "Mick", "Fanning")
    user3_id = user3["auth_user_id"]
    # Make public channel
    public_channel = channels_create_v1(user1_id, "Rainbow Six Siege Community", True)
    public_channel_id = public_channel["channel_id"]
    # Make private channel
    private_channel = channels_create_v1(user1_id, "Minecraft", False)
    private_channel_id = private_channel["channel_id"]
    
    values = {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "user3_id": user3_id,
        "public_channel_id": public_channel_id,
        "private_channel_id": private_channel_id
    }
    return values

# channel_id does not refer to a valid channel
def test_invalid_channel(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]
    with pytest.raises(InputError):
        channel_details_v1(user1_id, 14)
    with pytest.raises(InputError):
        channel_details_v1(user2_id, 5234)

# the authorised user is not a member of the channel
def test_auth_user_not_in_channel(initial_data):
    user2_id = initial_data["user2_id"]
    user3_id = initial_data["user3_id"]
    public_channel_id = initial_data["public_channel_id"]
    with pytest.raises(AccessError):
        channel_details_v1(user2_id, public_channel_id)
    with pytest.raises(AccessError):
        channel_details_v1(user3_id, public_channel_id)

# test user is invalid and channel is valid
def test_user_invalid_and_channel_valid(initial_data):
    public_channel_id = initial_data["public_channel_id"]
    with pytest.raises(InputError):
        channel_details_v1(4345, public_channel_id)
    with pytest.raises(InputError):
        channel_details_v1(15, public_channel_id)

# the authorised user is not a member of the channel and channel_id is invalid
def test_user_not_in_channel_and_invalid_channel_id(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]
    with pytest.raises(InputError):
        channel_details_v1(user1_id, 5647)
    with pytest.raises(InputError):
        channel_details_v1(user2_id, 3)

# the authorised user is invalid and channel_id is invalid
def test_invalid_user_and_channel_id(initial_data):
    with pytest.raises(InputError):
        channel_details_v1(4, 15)
    with pytest.raises(InputError):
        channel_details_v1(1543, 555)

# testing showing details of public channel
def test_channel_details_v1_shows_public_channel_details(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]
    public_channel_id = initial_data["public_channel_id"]
    channel_join_v1(user2_id, public_channel_id)
    
    details = channel_details_v1(user1_id, public_channel_id)
    assert(details["is_public"] == True)
    assert(details["name"] == "Rainbow Six Siege Community")
    members_list = details["all_members"] 
    assert(len(members_list) == 2)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 1)

# testing showing details of private channel
def test_channel_details_v1_shows_private_channel_details(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]
    private_channel_id = initial_data["private_channel_id"]
    channel_invite_v1(user1_id, private_channel_id, user2_id)
    
    details = channel_details_v1(user1_id, private_channel_id)
    assert(details["is_public"] == False)
    assert(details["name"] == "Minecraft")
    members_list = details["all_members"] 
    assert(len(members_list) == 2)
    owner_members_list = details["owner_members"]
    assert(len(owner_members_list) == 1)



