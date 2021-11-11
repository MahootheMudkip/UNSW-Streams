import pytest
import requests
import json
from src.config import url
from src.gen_timestamp import get_curr_timestamp
import time

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200

@pytest.fixture
def data():
    # clear 
    requests.delete(url + 'clear/v1')

    # create a user 
    response1 = requests.post(url + "auth/register/v2", 
    json={
        "email": "Pink@Floyd.com",
        "password": "qtu4h35",
        "name_first": "Floyd",
        "name_last": "Pink"

    })
    token1 = response1.json()["token"]
    user1_id = response1.json()["auth_user_id"]

    # create a user 
    response2 = requests.post(url + "auth/register/v2", 
    json={
        "email": "AC@DC.com",
        "password": "iuywqro3",
        "name_first": "AC",
        "name_last": "DC"
    })
    token2 = response2.json()["token"]
    user2_id = response2.json()["auth_user_id"]
    
    # create a user 
    response3 = requests.post(url + "auth/register/v2", 
    json={
        "email": "Brian@May.com",
        "password": "wreqro3",
        "name_first": "Brian",
        "name_last": "May"
    })
    token3 = response3.json()["token"]
    user3_id = response3.json()["auth_user_id"]

    #create a dm 1
    dm1_response = requests.post(url + "dm/create/v1", 
    json={
        "token": token1,
        "u_ids": [user2_id]
    })
    dm1_id = dm1_response.json()["dm_id"]

    #create a dm 2
    dm2_response = requests.post(url + "dm/create/v1", 
    json={
        "token": token2,
        "u_ids": [user1_id, user3_id]
    })
    dm2_id = dm2_response.json()["dm_id"]

    #get a unix timestamp of the current time
    timestamp = get_curr_timestamp()

    return {
        "token1" : token1,
        "token2" : token2,
        "token3" : token3,
        "dm1_id" : dm1_id,
        "dm2_id" : dm2_id,
        "timestamp" : timestamp
    }

# testing valid token, invalid dm_id
def test_message_sendlaterdm_invalid_dm_id(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600

    response = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        data["token1"],
        "dm_id":        -4543,
        "message":      "jello",
        "time_sent" :   timestamp
    })
    assert response.status_code == INPUT_ERROR

# testing invalid token, valid dm_id
def test_message_sendlaterdm_invalid_token(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600

    response = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        "yyoyoyo",
        "dm_id":        data["dm1_id"],
        "message":      "Don't send this",
        "time_sent" :   timestamp
    })
    assert response.status_code == ACCESS_ERROR

# testing token and dm_id both invalid
def test_message_sendlaterdm_invalid_token_and_dm_id(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600

    response = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        "pssst",
        "dm_id":        -45857,
        "message":      "zoop",
        "time_sent" :   timestamp
    })
    assert response.status_code == ACCESS_ERROR


#when a user not in dm tries to send a message
def test_message_sendlaterdm_unauthorised_user(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600

    response = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        data["token3"],
        "dm_id":        data["dm1_id"],
        "message":      "Not this either",
        "time_sent" :   timestamp
    })
    assert response.status_code == ACCESS_ERROR

#testing when message is invalid (len > 1000)
def test_msg_sendlaterdm_invalid_message(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600

    response = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        data["token1"],
        "dm_id":        data["dm1_id"],
        "message":      "Don't" * 1100,
        "time_sent":    timestamp
    })
    assert response.status_code == INPUT_ERROR

#testing when message is sent in the past
def test_msg_sendlaterdm_past_message(data):
    #get a time stamp of one hour before curent time 
    timestamp = data["timestamp"] - 3600

    response = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        data["token2"],
        "dm_id":        data["dm1_id"],
        "message":      "Nope",
        "time_sent" :   timestamp
    })
    assert response.status_code == INPUT_ERROR


#testing if the message was sent before it was supposed to
def test_msg_sendlaterdm_check(data):
    #send a message 3 seconds from now
    timestamp = data["timestamp"] + 3
    response1 = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        data["token2"],
        "dm_id":        data["dm2_id"],
        "message":      "Don't send yet",
        "time_sent" :   timestamp
    })
    assert response1.status_code == NO_ERROR

    #sleep for 1 second and check if the msg was sent before 3 seconds
    time.sleep(1)
    response2 = requests.get(url + "dm/messages/v1", 
    params={
        "token": data["token3"],
        "dm_id":data["dm2_id"],
        "start": 0
    })
    
    message = response2.json()["messages"]
    assert message == []

#testing if the message was actually sent
def test_msg_sendlaterdm_verify(data):
    #send a message 2 seconds from now
    timestamp = data["timestamp"] + 2
    response1 = requests.post(url + "message/sendlaterdm/v1", 
    json={
        "token":        data["token2"],
        "dm_id":        data["dm2_id"],
        "message":      "Send it",
        "time_sent" :   timestamp
    })
    assert response1.status_code == NO_ERROR

    #sleep for 10 seconds and check if the message was sent
    time.sleep(2)
    response2 = requests.get(url + "dm/messages/v1", 
    params={
        "token": data["token1"],
        "dm_id": data["dm2_id"],
        "start": 0
    })
    
    message = response2.json()["messages"]
    assert message[0]["message"] == "Send it"


