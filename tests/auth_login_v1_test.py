import pytest

from src.error import InputError
from src.auth import auth_login_v1, auth_register_v1
from src.other import clear_v1

# fixture clears data_store and registers a user using valid details
@pytest.fixture
def register():
    clear_v1()
    register_return = auth_register_v1("email1@gmail.com", "password", "John", "Smith")
    id1 = register_return["auth_user_id"]

    register_return = auth_register_v1("email2@gmail.com", "password2", "Bob", "Jones")
    id2 = register_return["auth_user_id"]

    register_return = auth_register_v1("email3@gmail.com", "password3", "Adam", "White")
    id3 = register_return["auth_user_id"]
    
    return {
        "user1" : id1,
        "user2" : id2,
        "user3" : id3  
    }
# login with an unregistered email
def test_login_invalid_email(register):
    with pytest.raises(InputError):
        auth_login_v1("unregisteredemail@gmail.com", "password")

# login with incorrect password
def test_login_invalid_password(register):
    with pytest.raises(InputError):
        auth_login_v1("email1@gmail.com", "wrong password")

# login with registered emails and password results in same auth_user_id
# as given during registration
def test_login_can_login(register):
    login_return = auth_login_v1("email1@gmail.com", "password")
    returned_id = login_return["auth_user_id"]
    assert register["user1"] == returned_id

    login_return = auth_login_v1("email2@gmail.com", "password2")
    returned_id = login_return["auth_user_id"]
    assert register["user2"] == returned_id

    login_return = auth_login_v1("email3@gmail.com", "password3")
    returned_id = login_return["auth_user_id"]
    assert register["user3"] == returned_id
