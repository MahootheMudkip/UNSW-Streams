import json
import pytest
import requests
from src.config import url

INPUT_ERROR = 400

@pytest.fixture
def register():
    requests.delete(url + "clear/v1")

    user1_info = {
        "email" : "email1@gmail.com", 
        "password" : "password1",
        "name_first" : "John",
        "name_last" : "Smith" 
    }
    user2_info = {
        "email" : "email2@gmail.com", 
        "password" : "password2",
        "name_first" : "Bob",
        "name_last" : "Jones" 
    }
    user3_info = {
        "email" : "email3@gmail.com", 
        "password" : "password3",
        "name_first" : "Adam",
        "name_last" : "White" 
    }
    response1 = requests.post(url + "auth/register/v2", json=user1_info)
    id1 = response1.json()["auth_user_id"]
    tok1 = response1.json()["token"]

    response2 = requests.post(url + "auth/register/v2", json=user2_info)
    id2 = response2.json()["auth_user_id"]

    response3 = requests.post(url + "auth/register/v2", json=user3_info)
    id3 = response3.json()["auth_user_id"]

    return {
        "id1" : id1,
        "id2" : id2,
        "id3" : id3,
        "tok1": tok1
    }

# login with an unregistered email
def test_login_invalid_email(register):
    response = requests.post(url + "auth/login/v2", json={"email":"unregisteredemail@gmail.com", "password":"password"})
    assert response.status_code == INPUT_ERROR

# login with incorrect password
def test_login_invalid_password(register):
    response = requests.post(url + "auth/login/v2", json={"email":"email1@gmail.com", "password":"wrong password"})
    assert response.status_code == INPUT_ERROR

# login with registered emails and password results in same auth_user_id
# as given during registration
def test_login_can_login(register):
    response = requests.post(url + "auth/login/v2", json={"email":"email1@gmail.com", "password":"password1"})
    assert response.json()["auth_user_id"] == register["id1"]

    response = requests.post(url + "auth/login/v2", json={"email":"email2@gmail.com", "password":"password2"})
    assert response.json()["auth_user_id"] == register["id2"]

    response = requests.post(url + "auth/login/v2", json={"email":"email3@gmail.com", "password":"password3"})
    assert response.json()["auth_user_id"] == register["id3"]

# logging in multiple times result in different sessions which have differnt tokens
def test_different_token(register):
    response = requests.post(url + "auth/login/v2", json={"email":"email1@gmail.com", "password":"password1"})
    login_token = response.json()["token"]
    assert register["tok1"] != login_token

    response2 = requests.post(url + "auth/login/v2", json={"email":"email1@gmail.com", "password":"password1"})
    login_token2 = response2.json()["token"]
    assert login_token2 != login_token
