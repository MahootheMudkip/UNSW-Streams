import pytest
import requests
from src.config import url
import json
from datetime import *

INPUT_ERROR = 400
ACCESS_ERROR = 403
NO_ERROR = 200
# error status codes
URL = url + "standup/send/v1"

        # "user0_token":          user0_token,
        # "user1_token":          user1_token,
        # "user2_token":          user2_token,
        # "user2_id":             user2_id,
        # "public_channel_id":    public_channel_id,
        # "private_channel_id":   private_channel_id

@pytest.fixture
def initial_setup():
    # clear all stored data
    requests.delete(url + "clear/v1")

    # url routes
    auth_register_url = url + "auth/register/v2"
    channel_create_url = url + "channels/create/v2"

    # create new user 0, (global owner) and extracts token
    user0_response = requests.post(auth_register_url, json={      
        "email":        "theboss@gmail.com", 
        "password":     "999999",
        "name_first":   "Big", 
        "name_last":    "Boss"
    })
    user0 = user0_response.json()
    user0_token = user0["token"]
    user0_id = user0["auth_user_id"]

    # create new user 1 and extract token
    user1_response = requests.post(auth_register_url, json={      
        "email":        "lmao@gmail.com", 
        "password":     "123789",
        "name_first":   "Jeremy", 
        "name_last":    "Clarkson"
    })
    user1 = user1_response.json()
    user1_token = user1["token"]

    # create new user 2 and extract token
    user2_response = requests.post(auth_register_url, json={      
        "email":        "wtf@gmail.com", 
        "password":     "234789",
        "name_first":   "James",
        "name_last":    "May"
    })
    user2 = user2_response.json()
    user2_token = user2["token"]
    user2_id = user2["auth_user_id"]

    # create new user 3 and extract token
    user3_response = requests.post(auth_register_url, json={      
        "email":        "wt@gmail.com", 
        "password":     "234789",
        "name_first":   "Jame",
        "name_last":    "Ma"
    })
    user3 = user3_response.json()
    user3_token = user3["token"]

    # create public channel and extract channel_id
    public_channel_response = requests.post(channel_create_url, json={
        "token":        user1_token,
        "name":         "public_channel",
        "is_public":    True
    })
    public_channel = public_channel_response.json()
    public_channel_id = public_channel["channel_id"]

    # create private channel and extract channel_id
    private_channel_response = requests.post(channel_create_url, json={
        "token":        user1_token,
        "name":         "public_channel",
        "is_public":    False
    })
    private_channel = private_channel_response.json()
    private_channel_id = private_channel["channel_id"]

    return {
        "user0_token":          user0_token,
        "user0_id":             user0_id,
        "user1_token":          user1_token,
        "user2_token":          user2_token,
        "user3_token":          user3_token,
        "user2_id":             user2_id,
        "public_channel_id":    public_channel_id,
        "private_channel_id":   private_channel_id,
    }

# testing valid token, invalid channel_id
def test_message_send_v1_invalid_channel_id(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   -34587678,
        "message":      "hello world"
    })
    assert response.status_code == INPUT_ERROR

# testing invalid token, valid public channel_id
def test_message_send_v1_invalid_token_public(initial_setup):
    public_channel = initial_setup["public_channel_id"]
    response = requests.post(URL, json={
        "token":        "kjkjd",
        "channel_id":   public_channel,
        "message":      "hello world"
    })
    assert response.status_code == ACCESS_ERROR

# testing invalid token, valid private channel_id
def test_message_send_v1_invalid_token_private(initial_setup):
    private_channel = initial_setup["private_channel_id"]
    response = requests.post(URL, json={
        "token":        "kjkjd",
        "channel_id":   private_channel,
        "message":      "hello world"
    })
    assert response.status_code == ACCESS_ERROR

# testing global user (not a member) trying to access valid channel
def test_message_send_v1_global_user_not_member(initial_setup):
    user0_token = initial_setup["user0_token"]
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.post(URL, json={
        "token":        user0_token,
        "channel_id":   public_channel,
        "message":      "hello world"
    })

    response2 = requests.post(URL, json={
        "token":        user0_token,
        "channel_id":   private_channel,
        "message":      "hello world"
    })

    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

# testing normal user (not a member) trying to access valid channel
def test_message_send_v1_unauthorised_user(initial_setup):
    user2_token = initial_setup["user2_token"]
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   public_channel,
        "message":      "hello world"
    })

    response2 = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   private_channel,
        "message":      "hello world"
    })

    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

# token and channel_id both invalid
def test_message_send_v1_invalid_token_and_channel_id(initial_setup):
    response = requests.post(URL, json={
        "token":        "4534",
        "channel_id":   -45857,
        "message":      "hello world"
    })
    assert response.status_code == ACCESS_ERROR

# invalid user, valid channel_id, invalid message
def test_message_send_v1_invalid_token_and_message(initial_setup):
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.post(URL, json={
        "token":        "fake",
        "channel_id":   public_channel,
        "message":      ""
    })

    response2 = requests.post(URL, json={
        "token":        "fake",
        "channel_id":   private_channel,
        "message":      "a"*1001
    })

    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

# valid user, invalid channel, invalid message
def test_message_send_v1_invalid_channel_id_and_message(initial_setup):
    user1_token = initial_setup["user1_token"]

    response1 = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   -3423,
        "message":      ""
    })

    response2 = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   3563645,
        "message":      "z" * 1001
    })

    assert response1.status_code == INPUT_ERROR
    assert response2.status_code == INPUT_ERROR

# valid user and channel_id, user not in channel, message invalid
def test_message_send_v1_user_not_member_and_invalid_message(initial_setup):
    user2_token = initial_setup["user2_token"]
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   public_channel,
        "message":      ""
    })

    response2 = requests.post(URL, json={
        "token":        user2_token,
        "channel_id":   private_channel,
        "message":      "#" * 1001
    })

    assert response1.status_code == ACCESS_ERROR
    assert response2.status_code == ACCESS_ERROR

# valid user and channel_id, invalid message
def test_message_send_v1_invalid_message(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel = initial_setup["public_channel_id"]
    private_channel = initial_setup["private_channel_id"]

    response1 = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   public_channel,
        "message":      ""
    })

    response2 = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   private_channel,
        "message":      "#" * 1001
    })

    assert response1.status_code == INPUT_ERROR
    assert response2.status_code == INPUT_ERROR

# valid user and channel_id, message over 1000 characters
def test_message_send_v1_message_too_long(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel = initial_setup["public_channel_id"]

    response1 = requests.post(URL, json={
        "token":        user1_token,
        "channel_id":   public_channel,
        "message":      """111111111111111111111111111111111111111111dcjdnajvbdvubadvndjnszjncjdsvnkdsnvujnfdusvbjfsnvndksnvose
                            dbsdjfbdhsbfhdbsnfbdhfbdsbfdnjsfbjdsfdjsnfudnskjbfdbfjsbdfjsdkbfdjkmsnfnbdisbfdpisfjdksnfjdksfvbsce
                            jsdsdjsbchdsjbcdsjchcdshdbcsjhbdhjjcsbdhjsbcdhjsbhjcdbhjsbhjcbsdccsjcndhsbcudwiuefiuwhbcdncwibvchdw
                            bhcbwicnjdnwsknuiwbwjdiwfwinbfhwwuwfdbsdjfbdhsbfhdbsnfbdhfbdsbfdnjsfbjdsfdjsnfudnskjbfdbfjsbdfjsdke
                            bfdjkmsnfnbdisbfdpisfjdksnfjdksfvbscssbcahsdbcusbjasuiahcudahjcndabcudbaubcydbahdbcuadbucbdbaucbdye
                            jsdsdjsbchdsjbcdsjchcdshdbcsjhbdhjjcsbdhjsbcdhjsbhjcdbhjsbhjcbsdccsjcndhsbcudwiuefiuwhbcdncwibvchdw
                            bhcbwicnjdnwsknuiwbwjdiwfwinbfhwwuwfdbsdjfbdhsbfhdbsnfbdhfbdsbfdnjsfbjdsfdjsnfudnskjbfdbfjsbdfjsdkb
                            fdjkmsnfnbdisbfdpisfjdksnfjdksfvbscjsdsdjsbchdsjbcdsjchcdshdbcsjhbdhjjcsbdhjsbcdhjsbhjcdbhjsbhjcbsd
                            csjcndhsbcudwiuefiuwhbcdncwibvchdwbhcbwicnjdnwsknuiwbwjdiwfwinbfhwwuwfdbsdjfbdhsbfhdbsnfbdhfbdsbfdn
                            sfbjdsfdjsnfudnskjbfdbfjsbdfjsdkbfdjkmsnfnbdisbfdpisfjdksnfjdksfvbscjsdsdjsbchdsjbcdsjchcdshdbcsjhb
                            hjjcsbdhjsbcdhjsbhjcdbhjsbhjcbsdccsjcndhsbcudwiuefiuwhbcdncwibvchdwbhcbwicnjdnwsknuiwbwjdiwfwinbfhw
                            uwfdbsdjfbdhsbfhdbsnfbdhfbdsbfdnjsfbjdsfdjsnfudnskjbfdbfjsbdfjsdkbfdjkmsnfnbdisbfdpisfjdksnfjdksfvb
                            cjsdsdjsbchdsjbcdsjchcdshdbcsjhbdhjjcsbdhjsbcdhjsbhjcdbhjsbhjcbsdccsjcndhsbcudwiuefiuwhbcdncwibvchd
                            bhcbwicnjdnwsknuiwbwjdiwfwinbfhwwuwfaaasajndsyabdsybabsydyhygye7weguh92e7eajuancaisamazing123456"""
    })


    assert response1.status_code == INPUT_ERROR

# no active standup, all else valid
def test_standup_send_v1_no_active_standup(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel_id = initial_setup["public_channel_id"]

    resp = requests.get(url + "standup/active/v1", params={"token": user1_token, "channel_id": public_channel_id})
    assert(resp.status_code == NO_ERROR)
    assert resp.json()["time_finish"] == None
    assert resp.json()["is_active"] == False

    resp = requests.post(URL, json={"token": user1_token, "channel_id": public_channel_id, "message": "foo"})
    assert(resp.status_code == INPUT_ERROR)

# messages are sent to message queue during standup
def test_standup_send_v1_message_queue(initial_setup):
    user1_token = initial_setup["user1_token"]
    public_channel_id = initial_setup["public_channel_id"]

    resp = requests.post(url + "standup/start/v1", json={"token": user1_token, "channel_id": public_channel_id, "length": 5})
    assert(resp.status_code == NO_ERROR)
    
    for i in range(3):
        response1 = requests.post(URL, json={
            "token":        user1_token,
            "channel_id":   public_channel_id,
            "message":      str(i)
        })
        assert response1.status_code == NO_ERROR
    

