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
    # Make public channel
    public_channel = channels_create_v1(user1_id, "Rainbow Six Siege Community", True)
    public_channel_id = public_channel["channel_id"]
    # Make private channel
    private_channel = channels_create_v1(user1_id, "Minecraft", False)
    private_channel_id = private_channel["channel_id"]
    values = {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "public_channel_id": public_channel_id,
        "private_channel_id": private_channel_id
    }
    return values

# channel_id does not refer to a valid channel.
def test_invalid_channel(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]
    with pytest.raises(InputError):
        channel_invite_v1(user1_id, 14, user2_id) 

# u_id does not refer to a valid user.
def test_invalid_u_id(initial_data):
    user1_id = initial_data["user1_id"]
    public_channel_id = initial_data["public_channel_id"]
    with pytest.raises(InputError):
        channel_invite_v1(user1_id, public_channel_id, 5)    

# auth_user_id does not refer to a valid user.
def test_invalid_auth_user_id(initial_data):
    user2_id = initial_data["user2_id"]
    public_channel_id = initial_data["public_channel_id"]
    with pytest.raises(InputError):
        channel_invite_v1(3, public_channel_id, user2_id)
    with pytest.raises(InputError):
        channel_invite_v1(532, public_channel_id, user2_id)

# channel_id and u_id are invalid
def test_invalid_u_id_and_channel_id(initial_data):
    user1_id = initial_data["user1_id"]
    with pytest.raises(InputError):
        channel_invite_v1(user1_id, 4, 5)
    with pytest.raises(InputError):
        channel_invite_v1(user1_id, 243, 763)   

# auth_user_id and u_id are invalid
def test_invalid_auth_user_id_and_u_id(initial_data):
    public_channel_id = initial_data["public_channel_id"]
    with pytest.raises(InputError):
        channel_invite_v1(6, public_channel_id, 15)
    with pytest.raises(InputError):
        channel_invite_v1(432, public_channel_id, 352)

# auth_user_id and channel_id are invalid
def test_invalid_auth_user_id_and_channel_id(initial_data):
    user2_id = initial_data["user2_id"]
    with pytest.raises(InputError):
        channel_invite_v1(7, 4, user2_id)
    with pytest.raises(InputError):
        channel_invite_v1(432, 243, user2_id)

# All inputs are invalid
def test_invalid_inputs(initial_data):
    with pytest.raises(InputError):
        channel_invite_v1(7, 4, 6)
    with pytest.raises(InputError):
        channel_invite_v1(432, 243, 324)     

# user is already a member of the public channel.
def test_member_duplicate(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]
    public_channel_id = initial_data["public_channel_id"]
    channel_join_v1(user2_id, public_channel_id)
    with pytest.raises(InputError):
        channel_invite_v1(user1_id, public_channel_id, user2_id)

# auth_user (invitee) is not a member of the public channel.
def test_invalid_invitee(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]
    public_channel_id = initial_data["public_channel_id"]
    with pytest.raises(AccessError):
       channel_invite_v1(user2_id, public_channel_id, user1_id)

# Arguments are valid.
# User is not a member of the channel.
# Invitee is a member of the channel.

# test user invited to public channel
def test_can_invite_public(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]    
    public_channel_id = initial_data["public_channel_id"]

    channel_invite_v1(user1_id, public_channel_id, user2_id)

    details = channel_details_v1(user2_id, public_channel_id)
    assert(details["is_public"] == True)
    assert(details["name"] == "Rainbow Six Siege Community")
    members_list = details["all_members"]
    assert(len(members_list) == 2)

# test user invited to private channel
def test_can_invite_private(initial_data):
    user1_id = initial_data["user1_id"]
    user2_id = initial_data["user2_id"]    
    public_channel_id = initial_data["public_channel_id"]

    channel_invite_v1(user1_id, public_channel_id, user2_id)

    details = channel_details_v1(user2_id, public_channel_id)
    assert(details["is_public"] == False)
    assert(details["name"] == "Minecraft")
    members_list = details["all_members"]
    assert(len(members_list) == 2)