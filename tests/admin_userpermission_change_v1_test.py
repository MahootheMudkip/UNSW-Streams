import pytest
import requests
from requests.api import request
from src.config import url

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

OWNER_PID = 1
MEMBER_PID = 2

@pytest.fixture
def data():
    # clear used data
    requests.delete(url + 'clear/v1')

    # create user 1
    response1 = requests.post(url + "auth/register/v2", json={
        "email": "user1@gmail.com",
        "password": "password",
        "name_first": "Luke",
        "name_last": "Pierce"

    })
    token1 = response1.json()["token"]

    # create user 2
    response2 = requests.post(url + "auth/register/v2", json={
        "email": "user2@gmail.com",
        "password": "password",
        "name_first": "Artem",
        "name_last": "Wing"

    })
    token2 = response2.json()["token"]

    # create user 3
    response3 = requests.post(url + "auth/register/v2", json={
        "email": "user3@gmail.com",
        "password": "password",
        "name_first": "Vyn",
        "name_last": "Ritcher"

    })
    token3 = response3.json()["token"]

    # create user 4 
    response4 = requests.post(url + "auth/register/v2", json={
        "email": "user4@gmail.com",
        "password": "password",
        "name_first": "Marius",
        "name_last": "Von hagen"

    })
    token4 = response4.json()["token"]

    values = {
        "token1": token1,
        "token2": token2,
        "token3": token3,
        "token4": token4,
    }
    return values

# token user is not a global owner, valid u_id, valid permission_id
def test_permission_change_invalid_token(data):
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token2"],
        "u_id":             2,
        "permission_id":    OWNER_PID
    })
    assert response.status_code ==  ACCESS_ERROR

# valid token, invalid u_id, valid permission_id
def test_permission_change_invalid_u_id(data):
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token1"],
        "u_id":             "akaoekaoe",
        "permission_id":    OWNER_PID
    })
    assert response.status_code == INPUT_ERROR

# valid token, valid u_id, invalid permission_id
def test_permission_change_invalid_p_id(data):
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token1"],
        "u_id":             1,
        "permission_id":    -91299
    })
    assert response.status_code == INPUT_ERROR

# token user is not a global owner, invalid permission_id
def test_permission_change_invalid_p_id_invalid_token(data):
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token2"],
        "u_id":             2,
        "permission_id":    -91299
    })
    assert response.status_code == ACCESS_ERROR

# token user is not a global owner, invalid u_id
def test_permission_change_invalid_token_invalid_u_id(data):
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token2"],
        "u_id":             "iadia",
        "permission_id":    OWNER_PID
    })
    assert response.status_code == ACCESS_ERROR

# Last global owner is being changed to member permissions
def test_permission_change_last_owner(data):
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token1"],
        "u_id":             0,
        "permission_id":    MEMBER_PID
    })
    assert response.status_code == INPUT_ERROR

# Last global owner is being changed to owner permissions
def test_permission_change_last_owner_no_change(data):
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            data["token1"],
        "u_id":             0,
        "permission_id":    OWNER_PID
    })
    assert response.status_code == NO_ERROR

# user with permissions promoted to owner now have owner privileges
def test_permission_change_promotion(data):
    token1 = data["token1"]
    token2 = data["token2"]
    # check that user2 initially can't use admin remove (member permissions)
    response = requests.delete(url + "admin/user/remove/v1", json={
        "token":    token2,
        "u_id":     2
    })
    assert response.status_code == ACCESS_ERROR

    # change user2's permissions into global owner
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            token1,
        "u_id":             1,
        "permission_id":    OWNER_PID
    })
    assert response.status_code == NO_ERROR

    # check that user2 can now use admin remove (global permissions)
    response = requests.delete(url + "admin/user/remove/v1", json={
        "token":    token2,
        "u_id":     2
    })
    assert response.status_code == NO_ERROR

# user with permissions demoted to member no longer have owner permission
def test_permission_change_demotion(data):
    token1 = data["token1"]
    token2 = data["token2"]
    # change user2's permissions into global owner
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            token1,
        "u_id":             1,
        "permission_id":    OWNER_PID
    })
    assert response.status_code == NO_ERROR

    # check that user2 can now use admin remove (global permissions)
    response = requests.delete(url + "admin/user/remove/v1", json={
        "token":    token2,
        "u_id":     2
    })
    assert response.status_code == NO_ERROR

    # change user2's permissions back into member
    response = requests.post(url + "admin/userpermission/change/v1", json={
        "token":            token1,
        "u_id":             1,
        "permission_id":    MEMBER_PID
    })
    assert response.status_code == NO_ERROR

    # check that user2 can no longer use admin remove (member permissions)
    response = requests.delete(url + "admin/user/remove/v1", json={
        "token":    token2,
        "u_id":     3
    })
    assert response.status_code == ACCESS_ERROR