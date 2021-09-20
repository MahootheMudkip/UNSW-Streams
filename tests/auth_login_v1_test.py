import pytest

from src.error import InputError
from src.auth import auth_login_v1, auth_register_v1
from src.other import clear_v1

# fixture for clearing datastore
# must be run before each test so data from previous test do not carry over
@pytest.fixture
def clear():
    clear_v1()

# login with an unregistered email
def test_login_invalid_email(clear):
    auth_register_v1("email1@gmail.com", "password", "John", "Smith")
    with pytest.raises(InputError):
        auth_login_v1("email2@gmail.com", "password")

# login with incorrect password
def test_login_invalid_password(clear):
    auth_register_v1("validemail@gmail.com", "password", "John", "Smith")
    with pytest.raises(InputError):
        auth_login_v1("validemail@gmail.com", "wrong password")

# login with registered email and password results in same auth_user_id
# as given during registration
def test_login_can_login(clear):
    register_return = auth_register_v1("validemail@gmail.com", "password", "John", "Smith")
    registered_id = register_return["auth_user_id"]

    login_return = auth_login_v1("validemail@gmail.com", "password")
    returned_id = login_return["auth_user_id"]

    assert registered_id == returned_id
