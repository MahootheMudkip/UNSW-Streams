from src.config import url
import json 
import requests
import pytest

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

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

    # create a dm 
    response = requests.post(url + "dm/create/v1", json={
        "token": token1,
        "u_ids": [1, 2, 3]
    })
    dm_id = response.json()["dm_id"]

    # send a message in that dm
    response = requests.post(url + "message/senddm/v1", json={
        "token": token1,
        "dm_id": 0,
        "message": "valid message"
    })
    message_id = response.json()["message_id"]

    values = {
        "token1": token1,
        "token2": token2,
        "token3": token3,
        "token4": token4,
        "dm_id": dm_id,
        "message_id": message_id
    }

    return values

# testing with invalid message_id, valid react_id
def test_invalid_message_id(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": 121239,
        "react_id": 1
    })
    assert response.status_code == INPUT_ERROR

# testing with invalid react_id, valid message_id
def test_invalid_react_id(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 51218
    })
    assert response.status_code == INPUT_ERROR

# testing with invalid react_id and invalid message_id
def test_invalid_both(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": 93198,
        "react_id": 51218
    })
    assert response.status_code == INPUT_ERROR

# checking to see if a single react can be viewed using dm_messages
def test_valid_single_react(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == NO_ERROR

    response = requests.get(url + "dm/messages/v1", params={
        "token": data["token1"],
        "dm_id": data["dm_id"],
        "start": 0
    })

    reacts = response.json()["messages"][0]["reacts"]
    assert reacts[0]["react_id"] == 1
    assert reacts[0]["u_ids"] == [0]
    assert reacts[0]["is_this_user_reacted"] == True

# checking to see if multiple reacts can be viewed using dm_messages
def test_valid_multiple_react(data):
    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == NO_ERROR

    response = requests.post(url + "message/react/v1", json={
        "token": data["token2"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == NO_ERROR

    response = requests.post(url + "message/react/v1", json={
        "token": data["token3"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == NO_ERROR

    response = requests.post(url + "message/react/v1", json={
        "token": data["token4"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == NO_ERROR

    response = requests.get(url + "dm/messages/v1", params={
        "token": data["token1"],
        "dm_id": data["dm_id"],
        "start": 0
    })

    reacts = response.json()["messages"][0]["reacts"]
    assert reacts[0]["react_id"] == 1
    assert reacts[0]["u_ids"] == [0, 1, 2, 3]
    assert reacts[0]["is_this_user_reacted"] == True

# testing when caller of dm/messages has not reacted to a message
def test_user_is_not_reacted(data):

    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == NO_ERROR

    response = requests.get(url + "dm/messages/v1", params={
        "token": data["token2"],
        "dm_id": data["dm_id"],
        "start": 0
    })

    reacts = response.json()["messages"][0]["reacts"]
    assert reacts[0]["react_id"] == 1
    assert reacts[0]["u_ids"] == [0]
    assert reacts[0]["is_this_user_reacted"] == False

# testing when caller of dm/messages has not reacted to a message
def test_user_already_reacted(data):

    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == NO_ERROR

    response = requests.post(url + "message/react/v1", json={
        "token": data["token1"], 
        "message_id": data["message_id"],
        "react_id": 1
    })
    assert response.status_code == INPUT_ERROR