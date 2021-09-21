import pytest

from src.other import clear_v1
from src.auth import auth_login_v1, auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1
from src.error import InputError
from src.error import AccessError

# fixture for registering and logging in user to avoid repetition.
@pytest.fixture
def clear_register_and_login():
    clear_v1()
    auth_register_v1("juanca.puyo@gmail.com", "27012003", "Juan", "Puyo")
    login_return = auth_login_v1("juanca.puyo@gmail.com", "27012003")
    return login_return

# channel_id does not refer to a valid channel.
def test_invalid_channel(clear_register_and_login):
    login_return = clear_register_and_login()
    auth_register_v1("tom.west@gmail.com", "27012003", "Tom", "West")
    login_return2 = auth_login_v1("tom.west@gmail.com", "27012003")
    create_return = channels_create_v1(login_return, "Minecraft", True)
    channel_join_v1(login_return2, create_return)
    with pytest.raises(InputError):
        channel_invite_v1(login_return, 14, login_return2) 

# u_id does not refer to a valid user.
def test_invalid_u_id(clear_register_and_login):
    register_return = clear_register_and_login()
    create_return = channels_create_v1(register_return, "Minecraft", True)
    with pytest.raises(InputError):
        channel_invite_v1(register_return, create_return, 5)    

# user is already a member of the channel.
def test_member_duplicate(clear_register_and_login):
    register_return = clear_register_and_login()
    register_return2 = auth_register_v1("tom.west@gmail.com", 27012003, "Tom", "West") 
    create_return = channels_create_v1(register_return, "Minecraft", True)
    channel_join_v1(register_return2, create_return)
    channel_invite_v1(register_return, create_return, register_return2)
    with pytest.raises(InputError):
        channel_invite_v1(register_return, create_return, register_return2)

# auth_user (invitee) is not a member of the channel.
def test_invalid_invitee(clear_register_and_login):
    register_return = clear_register_and_login
    register_return2 = auth_register_v1("tom.west@gmail.com", 27012003, "Tom", "West")
    create_return = channels_create_v1(register_return, "Minecraft", True)
    with pytest.raises(AccessError):
       channel_invite_v1(register_return, create_return, register_return2)

# Arguments are valid.
# User is not a member of the channel.
# Invitee is a member of the channel.

def test_can_invite(clear_register_and_login):
    login_return = clear_register_and_login
    auth_register_v1("tom.west@gmail.com", "27012003", "Tom", "West")
    invited = auth_login_v1("tom.west@gmail.com", "27012003")
    
    create_return = channels_create_v1(login_return, "Minecraft", True) 
    channel_join_v1(login_return, create_return)
    channel_invite_v1(login_return, create_return, invited)

    name, owners, members = channel_details_v1(login_return, create_return)
    assert invited in members 
