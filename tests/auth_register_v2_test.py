from tests.auth_logout_v2_test import NO_ERROR
import pytest
import requests
from src.config import url

INPUT_ERROR = 400
NO_ERROR = 200

@pytest.fixture
def clear():
    requests.delete(url + "clear/v1")

@pytest.fixture
def setup():
    requests.delete(url + "clear/v1")
    user1_info = {
        "email" : "validemail1@gmail.com", 
        "password" : "password",
        "name_first" : "John",
        "name_last" : "Smith" 
    }
    user2_info = {
        "email" : "validemail2@gmail.com", 
        "password" : "password",
        "name_first" : "John",
        "name_last" : "Smith" 
    }
    user3_info = {
        "email" : "validemail3@gmail.com", 
        "password" : "password",
        "name_first" : "John",
        "name_last" : "Smith" 
    }
    response1 = requests.post(url + "auth/register/v2", json=user1_info)
    id1 = response1.json()["token"]

    response2 = requests.post(url + "auth/register/v2", json=user2_info)
    id2 = response2.json()["token"]

    response3 = requests.post(url + "auth/register/v2", json=user3_info)
    id3 = response3.json()["token"]

    return {
        "id1" : id1,
        "id2" : id2,
        "id3" : id3
    }

# email does not match regex 
def test_register_email_invalid(clear):
    user_info = {
        "email" : "invalid_email.com",
        "password" : "password",
        "name_first" : "John", 
        "name_last" : "Smith"
    }
    response = requests.post(url + "auth/register/v2", json=user_info)
    assert response.status_code == INPUT_ERROR

# email has already been registered
def test_register_email_taken(clear):
    user_info = {
        "email" : "email@taken.com",
        "password" : "password",
        "name_first" : "John", 
        "name_last" : "Smith"
    }
    response = requests.post(url + "auth/register/v2", json=user_info)
    assert response.status_code == NO_ERROR
    response = requests.post(url + "auth/register/v2", json=user_info)
    assert response.status_code == INPUT_ERROR

# password under 6 characters
def test_register_password_invalid(clear):
    user_info = {
        "email" : "validemail@gmail.com",
        "password" : "pass",
        "name_first" : "John", 
        "name_last" : "Smith"
    }
    response = requests.post(url + "auth/register/v2", json=user_info)
    assert response.status_code == INPUT_ERROR

# first name < 1 character
def test_register_firstname_invalid(clear):
    user_info = {
        "email" : "validemail@gmail.com",
        "password" : "password",
        "name_first" : "", 
        "name_last" : "Smith"
    }
    response = requests.post(url + "auth/register/v2", json=user_info)
    assert response.status_code == INPUT_ERROR

# last name < 1 character
def test_register_lastname_invalid(clear):
    user_info = {
        "email" : "validemail@gmail.com",
        "password" : "password",
        "name_first" : "John", 
        "name_last" : ""
    }
    response = requests.post(url + "auth/register/v2", json=user_info)
    assert response.status_code == INPUT_ERROR

# users should have unique and valid handles according to handle generation rules
def test_register_handle_generation(setup):
    # register user 1, 2 and 3
    id1 = setup["id1"]
    id2 = setup["id2"]
    id3 = setup["id3"]

    # create channels for users 1, 2 and 3
    c_id1 = requests.post(url + "channels/create/v2", json={"token":id1, "name":"c1", "is_public":True}).json()["channel_id"]
    c_id2 = requests.post(url + "channels/create/v2", json={"token":id2, "name":"c2", "is_public":True}).json()["channel_id"]
    c_id3 = requests.post(url + "channels/create/v2", json={"token":id3, "name":"c3", "is_public":True}).json()["channel_id"]
    
    # request details for channels 1, 2 and 3
    d1 = requests.get(url + "channel/details/v2", params={"token":id1, "channel_id":c_id1}).json()
    d2 = requests.get(url + "channel/details/v2", params={"token":id2, "channel_id":c_id2}).json()
    d3 = requests.get(url + "channel/details/v2", params={"token":id3, "channel_id":c_id3}).json()

    # view details of owners (users 1 and 2) to verify their handles are different
    assert d1["owner_members"][0]["handle_str"] == "johnsmith"
    assert d2["owner_members"][0]["handle_str"] == "johnsmith0"
    assert d3["owner_members"][0]["handle_str"] == "johnsmith1"