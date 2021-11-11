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

    # create a user 
    response2 = requests.post(url + "auth/register/v2", 
    json={
        "email": "AC@DC.com",
        "password": "iuywqro3",
        "name_first": "AC",
        "name_last": "DC"
    })
    token2 = response2.json()["token"]
    
    # create a user 
    response3 = requests.post(url + "auth/register/v2", 
    json={
        "email": "Brian@May.com",
        "password": "wreqro3",
        "name_first": "Brian",
        "name_last": "May"
    })
    token3 = response3.json()["token"]

    #create a private channel
    channel1_response = requests.post(url + "channels/create/v2", 
    json={
        "token":        token1,
        "name":         "Channel1",
        "is_public":    False
    })
    channel1_id = channel1_response.json()["channel_id"]
    
    #create a public channel
    channel2_response = requests.post(url + "channels/create/v2", 
    json={
        "token":        token2,
        "name":         "Channel2",
        "is_public":    True
    })
    channel2_id = channel2_response.json()["channel_id"]

    #get a unix timestamp of the current time
    timestamp = get_curr_timestamp()

    return {
        "token1" : token1,
        "token2" : token2,
        "token3" : token3,
        "channel1_id" : channel1_id,
        "channel2_id" : channel2_id,
        "timestamp" : timestamp
    }

#testing when the token is invalid
def test_msg_sendlater_invalid_token(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600
    
    response = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        "yooyyo",
        "channel_id":   data["channel1_id"],
        "message":      "send this and you die",
        "time_sent" :   timestamp
    })
    assert response.status_code == ACCESS_ERROR

#testing when the channel is invalid 
def test_msg_sendlater_invalid_channelid(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600
    
    response = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        data["token1"],
        "channel_id":   -2394,
        "message":      "charge my phone",
        "time_sent" :   timestamp
    })
    assert response.status_code == INPUT_ERROR

#testing when both channel id and token are invalid
def test_msg_sendlater_invalid_token_channel(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600
    
    response = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        "Bwahaha",
        "channel_id":   -2394,
        "message":      "yooyyoyo",
        "time_sent" :   timestamp
    })
    assert response.status_code == ACCESS_ERROR

#testing when message is invalid (len > 1000)
def test_msg_sendlater_invalid_message(data):
    #get a time stamp one hour from now
    timestamp = data["timestamp"] + 3600

    response = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        data["token1"],
        "channel_id":   data["channel1_id"],
        "message":      "Don't" * 1100,
        "time_sent" :   timestamp
    })
    assert response.status_code == INPUT_ERROR

#testing when message is sent in the past
def test_msg_sendlater_past_message(data):
    #get a time stamp of one hour before curent time 
    timestamp = data["timestamp"] - 3600

    response = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        data["token1"],
        "channel_id":   data["channel1_id"],
        "message":      "Just do it" ,
        "time_sent" :   timestamp
    })
    assert response.status_code == INPUT_ERROR


#testing when user not a in channel, tries to send a msg
def test_msg_sendlater_user_notin_channel(data):
    #getting a time stamp two hours from now
    timestamp = data["timestamp"] + 7200
    
    response1 = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        data["token3"],
        "channel_id":   data["channel1_id"],
        "message":      "I'm lovin it",
        "time_sent" :   timestamp
    })
    
    response2 = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        data["token3"],
        "channel_id":   data["channel2_id"],
        "message":      "send this and you die",
        "time_sent" :   timestamp
    })

    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

#testing if the message was sent before it was supposed to
def test_msg_sendlate_check(data):
    #getting a time stamp 3 seconds from now
    timestamp = data["timestamp"] + 3

    response1 = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        data["token1"],
        "channel_id":   data["channel1_id"],
        "message":      "python",
        "time_sent" :   timestamp
    })
    assert response1.status_code == NO_ERROR

    #sleep for 1 second and check if the message was sent before 3 seconds
    time.sleep(1)
    response2 = requests.get(url + "channel/messages/v2", 
    params={
        "token": data["token1"],
        "channel_id": data["channel1_id"],
        "start": 0
    })
    
    message = response2.json()["messages"]
    assert message == []



#testing if the message was actually delivered
def test_msg_sendlater_verify(data):
    #getting a time stamp 2 seconds from now
    timestamp = data["timestamp"] + 2

    response1 = requests.post(url + "message/sendlater/v1", 
    json={
        "token":        data["token1"],
        "channel_id":   data["channel1_id"],
        "message":      "send this or you die",
        "time_sent" :   timestamp
    })
    assert response1.status_code == NO_ERROR

    #sleep for 2 seconds and check if the message was sent
    time.sleep(2)
    response2 = requests.get(url + "channel/messages/v2", 
    params={
        "token": data["token1"],
        "channel_id": data["channel1_id"],
        "start": 0
    })
    
    message = response2.json()["messages"]
    assert message[0]["message"] == "send this or you die"




    