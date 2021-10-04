import pytest

from src.error import InputError
from src.auth import auth_login_v1, auth_register_v1
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1

# fixture for clearing datastore
# must be run before each test so data from previous test do not carry over
@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def setup():
    clear_v1()
    register_return = auth_register_v1("validemail1@gmail.com", "password", "John", "Smith")
    id1 = register_return["auth_user_id"]

    register_return = auth_register_v1("validemail2@gmail.com", "password", "John", "Smith")
    id2 = register_return["auth_user_id"]

    return {
        "id1" : id1,
        "id2" : id2
    }

# email does not match regex 
def test_register_email_invalid(clear):
    with pytest.raises(InputError):
        auth_register_v1("invalid_email.com", "password", "John", "Smith")

# email has already been registered
def test_register_email_taken(clear):
    auth_register_v1("emailtaken@gmail.com", "password", "John", "Smith")
    with pytest.raises(InputError):
        auth_register_v1("emailtaken@gmail.com", "password", "John", "Smith")

# password under 6 characters
def test_register_password_invalid(clear):
    with pytest.raises(InputError):
        auth_register_v1("validemail@gmail.com", "pass", "John", "Smith")

# first name < 1 character
def test_register_firstname_invalid1(clear):
    with pytest.raises(InputError):
        auth_register_v1("validemail@gmail.com", "password", "", "Smith")

# first name > 50 characters
def test_register_firstname_invalid2(clear):
    with pytest.raises(InputError):
        auth_register_v1("validemail@gmail.com", "password", "V3WZTMoEqZHCo34AfMmuK87xvQb4a4XMu2gqNjR7pj0liUVzZG3", "Smith")

# last name < 1 character
def test_register_lastname_invalid(clear):
    with pytest.raises(InputError):
        auth_register_v1("validemail@gmail.com", "password", "John", "")

# last name > 50 characters
def test_register_lastname_invalid(clear):
    with pytest.raises(InputError):
        auth_register_v1("validemail@gmail.com", "password", "John", "V3WZTMoEqZHCo34AfMmuK87xvQb4a4XMu2gqNjR7pj0liUVzZG3")

# users should have unique u_id's
def test_register_different_uid(setup):

    assert setup["id1"] != setup["id2"]

# users should have unique and valid handles according to handle generation rules
def test_register_handle_generation(setup):
    # register user 1 and 2
    id1 = setup["id1"]
    id2 = setup["id2"]

    # create channels for users 1 and 2
    channel_id1 = channels_create_v1(id1, "channel1", True)["channel_id"]
    channel_id2 = channels_create_v1(id2, "channel2", True)["channel_id"]

    # request details for channels 1 and 2
    details1 = channel_details_v1(id1, channel_id1)
    details2 = channel_details_v1(id2, channel_id2)

    # view details of owners (users 1 and 2) to verify their handles are different
    user1_details = details1["owner_members"][0]
    user2_details = details2["owner_members"][0]
    assert user1_details["handle_str"] == "johnsmith"
    assert user2_details["handle_str"] == "johnsmith0"

# u_id returned is an integer
def test_register_is_int(setup):
    id = setup["id1"]

    assert type(id) == int 

# all parameters are valid:
# id obtained from login is same as id registered 
def test_register_can_login(setup):
    registered_id = setup["id1"]

    login_return = auth_login_v1("validemail1@gmail.com", "password")
    returned_id = login_return["auth_user_id"]

    assert registered_id == returned_id
 