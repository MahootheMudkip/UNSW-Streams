from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from datetime import *
import re

def message_send_v1(token, channel_id, message):
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
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    channels = store["channels"]

    # specified channel doesn't exist
    if channel_id not in channels.keys(): 
        raise InputError(description="Invalid channel_id")

    # if it reaches this point, the channel_id must be valid
    channel_info = channels[channel_id]
    channel_members = channel_info["all_members"]

    if auth_user_id not in channel_members:
        raise AccessError(description="Valid channel_id and authorised user not a member")

    if not 1 <= len(message) <= 1000:
        raise InputError(description="Invalid message length")

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
        "time_created": timestamp,
        "reacts":       [],
        "is_pinned":    False
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
        raise InputError(description="message_id not within a channel/dm that the user has joined")

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
                raise AccessError(description="Unauthorised user")
        else:
            if auth_user_id != location_info["owner"]:
                raise AccessError(description="Unauthorised user")
    
    # if it reaches this point, user has proper authorisation
    if len(message) > 1000:
        raise InputError(description="Message is too long")    
    
    # if message is empty, delete it 
    if len(message) == 0:
        location_info["messages"].remove(message_id)
        # this will work whether location_type is a channel or dm
        store["messages"].pop(message_id)
    else:
        message_info["message"] = message

    data_store.set(store)
    return {} 

def message_remove_v1(token, message_id):
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
    message_edit_v1(token, message_id, "")
    # this does the same thing
    return {}

# returns a list of type `messages` which contain the `query_str`.
def helper_search_v1(all_messages, message_list, auth_user_id, query_str):
    matches = []
    
    for message_id in message_list:
        message_info = all_messages[message_id]
        if re.search(query_str, message_info["message"]) != None:
            # valid match found
            matches.append(message_info)

    return matches

def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages in all of 
    the channels/DMs that the user has joined that contain the query.
    Note: pattern matching is CASE_SENSITIVE

    Arguments:
        token       (str): the given token
        query_str   (str): the given search query string

    Exceptions:
        InputError:
            - length of query_str is less than 1 or over 1000 characters
        AccessError:
            - auth_user_id is invalid (doesn't exist)

    Return Value:
        messages: List of dictionaries, where each dictionary 
            contains types { message_id, u_id, message, time_created }
    '''
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    # checking for valid query_str length
    if not 1 <= len(query_str) <= 1000:
        raise InputError(description="Invalid query_str")

    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]
    all_messages = store["messages"]

    matches = []
    # stores the valid messages which match the query string

    for channel in channels.values():
        if auth_user_id in channel["all_members"]:
            matches += helper_search_v1(all_messages, channel["messages"], auth_user_id, query_str)

    for dm in dms.values():
        if auth_user_id in dm["members"]:
            matches += helper_search_v1(all_messages, dm["messages"], auth_user_id, query_str)

    return {
        "messages": matches
    }

def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned".    

    Arguments:
        token       (str): the given token
        message_id  (int): the given message_id

    Exceptions:
        InputError:
            - message_id is not a valid message within a channel or DM 
                that the authorised user has joined
            - the message is already pinned
        AccessError:
            - message_id refers to a valid message in a joined channel/DM and 
                the authorised user does not have owner permissions in the channel/DM

    Return Value:
        empty dictionary.
    '''   
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]
    messages = store["messages"]
    users = store["users"]

    location_found_channel = False
    location_found_dm = False
    location_info = {}
    location_type = ""
    # check message_id is within a channel/dm that the user has joined

    # find location of message_id
    for channel in channels.values():
        if auth_user_id in channel["all_members"]:
            if message_id in channel["messages"]:
                location_found_channel = True
                channel_id = channel
                location_info = channel
                location_type = "channel"
                break
    
    if location_found_channel == False:
        for dm in dms.values():
            if auth_user_id in dm["members"]:
                if message_id in dm["messages"]:
                    location_found_dm = True
                    dm_id = dm
                    location_info = dm
                    location_type = "dm"
                    break
    
    if location_found_channel == False and location_found_dm == False:
        raise InputError(description="message_id not within a channel/dm that the user has joined")
    
    if messages[message_id]["is_pinned"] == True:
        raise InputError(description="The message is already pinned")
    
    # check if auth_user does not have owner permissions.
    if location_found_channel:
        channel_info = channel_id
        channel_all_members = channel_info["all_members"]
        channel_owners = channel_info["owner_members"]
        if users[auth_user_id]["is_owner"] == True:
            if auth_user_id not in channel_all_members:
                raise AccessError(description="Authorised User does not have owner permissions in the channel.")
        elif auth_user_id not in channel_owners:
            raise AccessError(description="Authorised User does not have owner permissions in the channel.")

    elif location_found_dm:
        dm_info = dm_id
        dm_members = dm_info["members"]
        dm_owner = dm_info["owner"]
        if users[auth_user_id]["is_owner"] == True:
            if auth_user_id not in dm_members:
                raise AccessError(description="Authorised User does not have owner permissions in the dm.")
        elif auth_user_id is not dm_owner:
           raise AccessError(description="Authorised User does not have owner permissions in the dm.")

    messages[message_id]["is_pinned"] = True
    data_store.set(store)
    return {}