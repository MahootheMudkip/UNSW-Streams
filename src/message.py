from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.user import notifications_send_reacted, notifications_send_tagged
from src.stats import *
from src.gen_timestamp import get_curr_timestamp
import re
import time, threading

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
    timestamp = get_curr_timestamp()

    # intitialise message's reacts
    react = {
        "react_id": 1,
        "u_ids": []
    }

    # send notifications to users tagged in message
    notifications_send_tagged(auth_user_id, message, channel_id, "channel")

    new_message = {
        "message_id":   message_id_tracker,
        "u_id":         auth_user_id,
        "message":      message,
        "time_created": timestamp,
        "reacts":       [react],
        "is_pinned":    False
    }

    # append new message_id to the channel messages list
    channel_messages.append(message_id_tracker)

    messages = store["messages"]
    messages[message_id_tracker] = new_message

    store["message_id_tracker"] = message_id_tracker + 1

    # Update user_stats and workspace_stats for messages_sent
    update_workspace_stats_messages("add")
    update_user_stats_messages(auth_user_id)

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
    for ch_id, channel in channels.items():
        if auth_user_id in channel["all_members"]:
            if message_id in channel["messages"]:
                location_found = True
                location_info = channel
                location_id = ch_id
                location_type = "channel"
                break
    
    if location_found == False:
        for dm_id, dm in dms.items():
            if auth_user_id in dm["members"]:
                if message_id in dm["messages"]:
                    location_found = True
                    location_info = dm
                    location_id = dm_id
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
        update_workspace_stats_messages("remove")
    else:
        notifications_send_tagged(auth_user_id, message, location_id, location_type)
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

# add user's reacts info to a list of messages based on if the caller_id has reacted to messages
def add_user_react_info(auth_user_id, messages):
    for message in messages:
        react = message["reacts"][0]
        react["is_this_user_reacted"] = auth_user_id in react["u_ids"]


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

    # Add info about if the caller user has reacted to each message in the list of messages
    add_user_react_info(auth_user_id, matches)

    return {
        "messages": matches
    }

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Send a message from the authorised user to the channel specified by channel_id,
    at a future unix timestamp given by user.

    Arguments:
        token       (str): the given token
        channel_id  (int): the given channel id
        message     (str): message text
        time_sent   (int): unix timestamp 

    Exceptions:
        InputError:
            - channel_id invalid (doesn't exist)
            - length of message is greater 1000 characters
            - timestamp given is of the past
        AccessError:
            - auth_user_id is invalid (doesn't exist)
            - channel_id is valid and the auth_user_id refers to a user
            who is not a member of the channel

    Return Value:
        message_id  (int): newly created message's id
    '''
    #get user id from token
    user_id = get_auth_user_id(token)

    store = data_store.get()
    channels = store["channels"]
    message_id_tracker = store["message_id_tracker"]
    
    #if channel doesn't exist
    if channel_id not in channels.keys(): 
        raise InputError (description = "Invalid channel id")
    
    #if user is not part of the channel
    all_members = channels[channel_id]["all_members"]
    if user_id not in all_members:
        raise AccessError (description = "User is not part of the channel")

    #get timestamp of the current time
    curr_timestamp = get_curr_timestamp()

    # if the given stamp is in the past
    if time_sent - curr_timestamp < 0:
        raise InputError (description = "Trying to send message in the past")
    
    #if the lenght of the message is greater than 1000 characters
    if len(message) > 1000:
       raise InputError (description = "Message is too long")

    react = {
        "react_id" : 1,
        "u_ids" : []
    }
    new_message = {
        "message_id":   message_id_tracker,
        "u_id":         user_id,
        "message":      message,
        "time_created": time_sent,
        "reacts":       [react],
        "is_pinned":    False

    } 
    
    #use the threading library to delay the message
    delay = time_sent - curr_timestamp
    t = threading.Timer(delay, helper_msg_sendlater,[channel_id, user_id, new_message])
    t.start()
    
    return {
        "message_id": message_id_tracker
    }
    
def helper_msg_sendlater(channel_id, user_id, new_message):
    '''
    Store the message in data store after a delay by threading function

    Arguments:
        channel_id       (int): the given channel id
        time_sent   (int): time at which message is to be sent
        new_message (dict): new message to be added and its other details
        
    Exceptions:
       None

    Return Value:
        None
    '''
    #load data store
    store = data_store.get()
    message_id_tracker = store["message_id_tracker"]
    channels = store["channels"]

    #add the new message to the data store
    all_messages = channels[channel_id]["messages"]
    all_messages.append(message_id_tracker)
    store["messages"][message_id_tracker] = new_message

    # send notifications to tagged users
    notifications_send_tagged(user_id, new_message["message"], channel_id, "channel")

    store["message_id_tracker"] = message_id_tracker + 1

    # Update user_stats and workspace stats for messages_sent
    update_workspace_stats_messages("add")
    update_user_stats_messages(user_id)

    data_store.set(store)

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
    
    if messages[message_id]["is_pinned"] == True:
        raise InputError(description="The message is already pinned")

    user_info = store["users"][auth_user_id] 
    user_is_owner = user_info["is_owner"]
    
    if location_type == "channel": 
        if auth_user_id not in location_info["owner_members"] and user_is_owner == False: 
            # not a owner or global owner 
            raise AccessError(description="Unauthorised user") 
    else: 
        if auth_user_id != location_info["owner"]: 
            raise AccessError(description="Unauthorised user") 

    messages[message_id]["is_pinned"] = True
    data_store.set(store)
    return {}

def message_unpin_v1(token, message_id):
    '''
    Given a message within a channel or DM, remove pin mark.    

    Arguments:
        token       (str): the given token
        message_id  (int): the given message_id

    Exceptions:
        InputError:
            - message_id is not a valid message within a channel or DM 
                that the authorised user has joined
            - the message is already not pinned
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
    
    if messages[message_id]["is_pinned"] == False:
        raise InputError(description="The message is already not pinned")

    user_info = store["users"][auth_user_id] 
    user_is_owner = user_info["is_owner"]
    
    if location_type == "channel": 
        if auth_user_id not in location_info["owner_members"] and user_is_owner == False: 
            # not a owner or global owner 
            raise AccessError(description="Unauthorised user") 
    else: 
        if auth_user_id != location_info["owner"]: 
            raise AccessError(description="Unauthorised user") 

    messages[message_id]["is_pinned"] = False
    data_store.set(store)
    return {}

def message_react_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, 
    add a "react" to that particular message.

    Arguments:
        token       (str): the given token
        message_id  (int): the given message_id
        react_id    (int): the type of react to add

    Exceptions:
        InputError:
            - message_id refers to an invalid message
            - react_id refers to an invalid react
            - the user has already reacted with that react type

    Return Value:
        empty dict
    '''
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    messages = store["messages"]

    # message_id is invalid
    if message_id not in messages:
        raise InputError(description="Message_id is invalid (doesn't exist)")

    # react_id is invalid
    if react_id != 1:
        raise InputError(description="React_id is invalid (doesn't exist)")
    
    # react_id must be 1
    reacts = messages[message_id]["reacts"][0]

    # add react from user if not already reacted
    if auth_user_id not in reacts["u_ids"]:
        notifications_send_reacted(auth_user_id, message_id)
        reacts["u_ids"].append(auth_user_id)
    else:
        # user already reacted
        raise InputError(description="User has already reacted with this reaction")
    
    data_store.set(store)
    return {}

def message_unreact_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, 
    remove a "react" from that particular message.

    Arguments:
        token       (str): the given token
        message_id  (int): the given message_id
        react_id    (int): the type of react to remove

    Exceptions:
        InputError:
            - message_id refers to an invalid message
            - react_id refers to an invalid react
            - the user has not yet reacted with that react type

    Return Value:
        empty dict
    '''
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    messages = store["messages"]

    # message_id is invalid
    if message_id not in messages:
        raise InputError(description="Message_id is invalid (doesn't exist)")

    # react_id is invalid
    if react_id != 1:
        raise InputError(description="React_id is invalid (doesn't exist)")
    
    # react_id must be 1
    reacts = messages[message_id]["reacts"][0]

    # user not yet reacted
    if auth_user_id not in reacts["u_ids"]:
        raise InputError(description="User has not yet reacted with this reaction")
    # remove react from user if already reacted
    else:
        reacts["u_ids"].remove(auth_user_id)
    
    data_store.set(store)
    return {}
