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

    