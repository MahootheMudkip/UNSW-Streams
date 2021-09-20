import pytest

from src.error import InputError
from src.auth import auth_login_v1, auth_register_v1
from src.other import clear_v1

# fixture for clearing datastore
# must be run before each test so data from previous test do not carry over
@pytest.fixture
def clear():
    clear_v1()

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

# users registered with different emails with same name
def test_register_different_uid(clear):
    register_return = auth_register_v1("validemail1@gmail.com", "password", "John", "Smith")
    id1 = register_return["auth_user_id"]

    register_return = auth_register_v1("validemail2@gmail.com", "password", "John", "Smith")
    id2 = register_return["auth_user_id"]

    assert id1 != id2

# all parameters are valid:
# id obtained from login is same as id registered 
def test_register_can_login(clear):
    register_return = auth_register_v1("validemail@gmail.com", "password", "John", "Smith")
    registered_id = register_return["auth_user_id"]

    login_return = auth_login_v1("validemail@gmail.com", "password")
    returned_id = login_return["auth_user_id"]

    assert registered_id == returned_id
 