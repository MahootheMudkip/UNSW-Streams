from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from datetime import *

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

    # if it reaches this point, a valid location has been found
    user_info = store["users"][auth_user_id]
    user_is_owner = user_info["is_owner"]
    
    message_info = store["messages"][message_id]
    message_u_id = message_info["u_id"]
    if auth_user_id != message_u_id:
        if location_type == "channel":
            if auth_user_id not in location_info["owner_members"] and user_is_owner == False:
                # not a owner or global owner
                raise AccessError("Unauthorised user")
        elif location_type == "dm":
            if auth_user_id != location_info["owner"] and user_is_owner == False:
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