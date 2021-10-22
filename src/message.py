from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from datetime import *


'''
Send a message from the authorised user to the channel specified by channel_id.

Arguments:
    token       (str): the given token
    channel_id  (int): the given channel id
    message     (str): message text

Exceptions:
    InputError:
        - channel_id invalid (doesn't exist)
        - length of message is less than 1 character or > 1000 characters
    AccessError:
        - auth_user_id is invalid (doesn't exist)
        - channel_id is valid and the auth_user_id refers to a user
          who is not a member of the channel

Return Value:
    message_id  (int): newly created message's id
'''
def message_send_v1(token, channel_id, message):
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    channels = store["channels"]

    # specified channel doesn't exist
    if channel_id not in channels.keys(): 
        raise InputError("Invalid channel_id")

    # if it reaches this point, the channel_id must be valid
    channel_info = channels[channel_id]
    channel_members = channel_info["all_members"]

    if auth_user_id not in channel_members:
        raise AccessError("Valid channel_id and authorised user not a member")

    if not 1 <= len(message) <= 1000:
        raise InputError("Invalid message length")

    # at this point, everything is valid
    message_id_tracker = store["message_id_tracker"]
    channel_messages = channel_info["messages"]

    # timestamp
    dt = datetime.now()
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

    new_message = {
        "message_id":   message_id_tracker,
        "u_id":         auth_user_id,
        "message":      message,
        "time_created": timestamp
    }

    # append new message_id to the channel messages list
    channel_messages.append(message_id_tracker)

    messages = store["messages"]
    messages[message_id_tracker] = new_message

    store["message_id_tracker"] = message_id_tracker + 1
    data_store.set(store)

    return {
        "message_id": message_id_tracker
    }

'''
Given a message, update its text with new text.
If the new message is an empty string, the message is deleted.

Arguments:
    token       (str): the given token
    message_id  (int): the given channel id
    message     (str): message text

Exceptions:
    InputError:
        - length of message is > 1000 characters
        - message_id does not refer to a valid message within a 
          channel/DM that the authorised user has joined
    AccessError:
        - auth_user_id is invalid (doesn't exist)
        AccessError is thrown if none of the following are true:
            - authorised user has owner permissions
            - message was made by the authorised user

Return Value:
    n/a
'''
def message_edit_v1(token, message_id, message):
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]

    location_found = False
    location_info = {}
    location_type = ""
    # check message_id is within a channel/dm that the user has joined

    # find location of message_id
    for channel in channels.values():
        if auth_user_id in channel["all_members"]:
            if message_id in channel["messages"]:
                location_found = True
                location_info = channel
                location_type = "channel"
                break
    
    if location_found == False:
        for dm in dms.values():
            if auth_user_id in dm["members"]:
                if message_id in dm["messages"]:
                    location_found = True
                    location_info = dm
                    location_type = "dm"
                    break
    
    if location_found == False:
        raise InputError("message_id not within a channel/dm that the user has joined")

    # if it reaches this point, the user is part of the channel/dm of the message
    # and a valid location has been found
    user_info = store["users"][auth_user_id]
    user_is_owner = user_info["is_owner"]
    
    message_info = store["messages"][message_id]
    message_u_id = message_info["u_id"]
    if auth_user_id != message_u_id:
        if location_type == "channel":
            if auth_user_id not in location_info["owner_members"] and user_is_owner == False:
                # not a owner or global owner
                raise AccessError("Unauthorised user")
        else:
            if auth_user_id != location_info["owner"]:
                raise AccessError("Unauthorised user")
    
    # if it reaches this point, user has proper authorisation
    if len(message) > 1000:
        raise InputError("Message is too long")    
    
    # if message is empty, delete it 
    if len(message) == 0:
        location_info["messages"].remove(message_id)
        # this will work whether location_type is a channel or dm
        store["messages"].pop(message_id)
    else:
        message_info["message"] = message

    data_store.set(store)
    return {} 

'''
Given a message, remove it from the channel/dm

Arguments:
    token       (str): the given token
    message_id  (int): the given channel id

Exceptions:
    InputError:
        - message_id does not refer to a valid message within a 
          channel/DM that the authorised user has joined
    AccessError:
        - auth_user_id is invalid (doesn't exist)
        AccessError is thrown if none of the following are true:
            - authorised user has owner permissions
            - message was made by the authorised user

Return Value:
    n/a
'''
def message_remove_v1(token, message_id):
    message_edit_v1(token, message_id, "")
    # this does the same thing
    return {}
