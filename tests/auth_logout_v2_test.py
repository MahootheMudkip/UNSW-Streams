from src.error import AccessError
from tests.channels_create_v1_test import ACCESS_ERROR
import pytest
import requests
from src.config import url

ACCESS_ERROR = 403
NO_ERROR = 200

@pytest.fixture
def setup():
    requests.delete(url + "clear/v1")
    user1_info = {
        "email" : "validemail1@gmail.com", 
        "password" : "password",
        "name_first" : "John",
        "name_last" : "Smith" 
    }
    response1 = requests.post(url + "auth/register/v2", json=user1_info)
    token1 = response1.json()["token"]

    return {
        "token1" : token1
    }

# token passed in is in invalid format
def test_auth_logout_invalid_token(setup):
    response = requests.post(url + "auth/logout/v1", json={"token":"invalid.token"})
    assert response.status_code == ACCESS_ERROR

# token passed in is expired
def test_auth_logout_expired_token(setup):
    response = requests.post(url + "auth/logout/v1", json={"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjAsInNlc3Npb25faWQiOjF9.-Wnws-wjpGCUnIOFSghZb4Bq4221MyeXJLvZBqr6MeM"})
    assert response.status_code == ACCESS_ERROR
 
# successful logout of 1 token, that token cannot be used to call other functions afterwards
def test_auth_logout_valid_token(setup):
    token1 = setup["token1"]

    # creating channel works fine when logged in
    response1 = requests.post(url + "channels/create/v2", json={"token":token1, "name":"channel1", "is_public":True})
    assert response1.status_code == NO_ERROR

    response = requests.post(url + "auth/logout/v1", json={"token":token1})
    assert response.status_code == NO_ERROR

    # error after token has been invalidated
    response1 = requests.post(url + "channels/create/v2", json={"token":token1, "name":"channel1", "is_public":True})
    assert response1.status_code == ACCESS_ERROR

# successful logout of 1 token, other tokens of that same user can still work
def test_auth_logout_multiple_sessions(setup):
    # login again (creates session 2)
    login_reponse1 = requests.post(url + "auth/login/v2", json={"email":"validemail1@gmail.com", "password":"password"})
    token1 = login_reponse1.json()["token"]

    # login again (creates session 3)
    login_reponse2 = requests.post(url + "auth/login/v2", json={"email":"validemail1@gmail.com", "password":"password"})
    token2 = login_reponse2.json()["token"]

    # logout of session 1
    token0 = setup["token1"]
    response = requests.post(url + "auth/logout/v1", json={"token":token0})
    assert response.status_code == NO_ERROR

    # create channel still works for other tokens
    response1 = requests.post(url + "channels/create/v2", json={"token":token1, "name":"channel1", "is_public":True})
    assert response1.status_code == NO_ERROR
    response1 = requests.post(url + "channels/create/v2", json={"token":token2, "name":"channel1", "is_public":True})
    assert response1.status_code == NO_ERROR
    response1 = requests.post(url + "channels/create/v2", json={"token":token0, "name":"channel1", "is_public":True})
    assert response1.status_code == ACCESS_ERROR

# logging out with a user token in the correct format but user doesn't exist
def test_token_correct_format_user_doesnt_exist(setup):
    response = requests.post(url + "auth/logout/v1", json={"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjJ9.oxK-flUTSSD_p8xE-WKgn6Q3Mp8oojh-RGCqj69JPE4"})
    assert response.status_code == ACCESS_ERROR