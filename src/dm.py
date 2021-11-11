from src.stats import *
from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.message import add_user_react_info
from src.user import notifications_send_tagged, notifications_send_invited
from src.gen_timestamp import get_curr_timestamp
import threading
import time

def dm_create_v1(token, u_ids):
    '''
    Creates a new Dm
    
    Arguments:
        token (str):            the given token
        u_ids (list of ints):   contains the user ids of people to be added in the dm
    
    Exceptions:
        InputError:
            - user_ids invalid (doesn't exist)

        AccessError:
            - token invalid
    
    Return Value:
        dm_id (int) 
    '''
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    users = store["users"]
    dm_id = store["dm_id_tracker"]

    #checking if all the u_ids are valid
    for id in u_ids:
        if id not in users.keys() or id == auth_user_id:
            raise InputError("user id is not valid")
    
    # getting values to be entred in the new dm
    u_ids.append(auth_user_id)
    dm_name = ", ".join(sorted([users[u_id]["handle_str"] for u_id in  u_ids]))

    #create dm
    dms[dm_id] = {
        "name" : dm_name,
        "owner" : auth_user_id,
        "members" : u_ids,
        "messages" : []
    }

    # send notification to all invitees
    for u_id in u_ids:
        if u_id != auth_user_id:
            notifications_send_invited(auth_user_id, u_id, dm_id, "dm")

    # Generate new Dm id and update data store dm id with the new dm_id
    store["dm_id_tracker"] += 1
    
    # Update workspace stats and user_stats for all users in new dm 
    update_workspace_stats_dms("add")
    for u_id in u_ids:
        update_user_stats_dms(u_id, "add")

    # Store the new dm back to data store
    data_store.set(store)
 
    return {
        "dm_id" : dm_id
    }
  
def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is a member of.
    
    Arguments:
        token (str):            the given token
        
    Exceptions:
        AccessError:
            - token invalid
    
    Return Value:
        A dictionary with dms as key and value being a list of DMs
        that the user is a member of.
    '''
    auth_user_id = get_auth_user_id(token)
    dm_list = []
    
    #extract data from data store
    store = data_store.get()
    dms = store["dms"]
    
    #check if the user is part of a dm
    #append the dm_is to dm list if they are
    for dm in dms.keys():
        if auth_user_id in dms[dm]["members"]:
            dm_list.append({"dm_id" : dm , "name" : dms[dm]["name"]})
    
    return {
        "dms" : dm_list
    }    

def dm_details_v1(token, dm_id ):
    '''
    Returns details of given dm_id.
    
    Arguments:
        token (str):            the given token
        dm_id (int):            the given dm_id
        
    Exceptions:
        AccessError:
            - token invalid
            - dm_id is valid and auth_user is not in dm.
        InputError:
            - dm_id is not valid.
    
    Return Value:
        name    (str):                the name of given dm_id.
        members (list of user dicts): list of members of the given dm_id.
    '''
    #get user id from a token
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    users = store["users"]

    #check if user dm id valid
    if dm_id not in dms:
        raise InputError("dm id not valid")

    #check if the user is part of the dm
    if auth_user_id not in dms[dm_id]["members"]:
        raise AccessError("user is not part of the dm")
    
    #extract details
    name = dms[dm_id]["name"]
    member_ids = dms[dm_id]["members"]
    members = []

    #append each member's details from users to members list
    #remove is_owner, password and sessions field
    for member_id in member_ids:
        # appending new_user dictionary
        user_info = users[member_id]
        user_copy = user_info.copy()
        # remove unecessary fields
        user_copy.pop("password")
        user_copy.pop("is_owner")
        user_copy.pop("sessions")
        user_copy.pop("notifications")
        user_copy.pop("user_stats")
        # add u_id item
        user_copy["u_id"] = member_id
    
        members.append(user_copy)
    
    return {
        "name" : name, 
        "members" : members
    }

def dm_remove_v1(token, dm_id):
    '''
    Removes the given dm_id.
    
    Arguments:
        token (str):            the given token
        dm_id (int):            the given dm_id
        
    Exceptions:
        AccessError:
            - token invalid
            - dm_id is valid and auth_user is not the owner.
        InputError:
            - dm_id is not valid.
    
    Return Value:
        Empty dictionary.
    '''
    #get user id from a token
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    
    #check if dm id is valid
    if dm_id not in dms:
        raise InputError("dm id not valid")

    #check if user is the owner
    if auth_user_id != dms[dm_id]["owner"]:
        raise AccessError("user not the owner of the dm")

    # Update user_stats for all users in removed dm and workspace stats
    update_workspace_stats_dms("remove")
    u_ids = dms[dm_id]["members"]
    for u_id in u_ids:
        update_user_stats_dms(u_id, "remove")

    #remove the dm
    del dms[dm_id]
    
    data_store.set(store)
    return {}


def dm_leave_v1(token, dm_id):
    '''
    Auth_user leaves specified dm_id.
    
    Arguments:
        token (str):            the given token
        dm_id (int):            the given dm_id
        
    Exceptions:
        AccessError:
            - token invalid
            - dm_id is valid and auth_user is not in dm.
        InputError:
            - dm_id is not valid.
    
    Return Value:
        Empty dictionary.
    '''
    #get user_id from token
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]

    #check if user dm id valid
    if dm_id not in dms:
        raise InputError("dm id not valid")

    #check if the user is part of the dm
    if auth_user_id not in dms[dm_id]["members"]:
        raise AccessError("user is not part of the dm")

    #remove the user
    dms[dm_id]["members"].remove(auth_user_id)

    # Update user_stats for all users in removed dm
    update_user_stats_dms(auth_user_id, "remove")

    data_store.set(store)

    return {}


def message_senddm_v1(token, dm_id, message):
    '''
    Send a message from the authorised user to the dm specified by dm_id.

    Arguments:
        token       (str): the given token
        dm_id       (int): the given dm id
        message     (str): message text

    Exceptions:
        InputError:
            - dm_id invalid (doesn't exist)
            - length of message is less than 1 character or > 1000 characters
        AccessError:
            - auth_user_id is invalid (doesn't exist)
            - dm_id is valid and the auth_user_id refers to a user
            who is not a member of the channel

    Return Value:
        message_id  (int): newly created message's id
    '''

    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]

    # specified dm doesn't exist
    if dm_id not in dms.keys(): 
        raise InputError("Invalid dm_id")

    # if it reaches this point, the dm_id must be valid
    dm_info = dms[dm_id]
    dm_members = dm_info["members"]

    if auth_user_id not in dm_members:
        raise AccessError("Valid dm_id and authorised user not a member")

    if not 1 <= len(message) <= 1000:
        raise InputError("Invalid message length")

    # at this point, everything is valid
    message_id_tracker = store["message_id_tracker"]
    dm_messages = dm_info["messages"]

    # timestamp
    timestamp = get_curr_timestamp()

    # intitialise message's reacts
    react = {
        "react_id": 1,
        "u_ids": []
    }

    # send notifications to users tagged in message
    notifications_send_tagged(auth_user_id, message, dm_id, "dm")

    new_message = {
        "message_id":   message_id_tracker,
        "u_id":         auth_user_id,
        "message":      message,
        "time_created": timestamp,
        "reacts":       [react],
        "is_pinned":    False
    }

    # append new message_id to the channel messages list
    dm_messages.append(message_id_tracker)

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


def dm_messages_v1(token, dm_id, start):
    '''
    Returns up to 50 messages between index "start" and "start + 50". 
    Message with index 0 is the most recent message in the dm. 
    This function returns a new index "end" which is the value of "start + 50" or
    -1 if there are no more messages to load after this return.

    Arguments:
        auth_user_id (int): the given authorised user id
        dm_id        (int): the given dm id
        start        (int): index to start returning messages from
                            (start is assumed to be >= 0)
    Exceptions:
        InputError:
            - dm_id invalid (doesn't exist)
            - start > total number of messages in channel
        AccessError:
            - auth_user_id is invalid (doesn't exist)
            - dm_id is valid and the auth_user_id refers to a user
            who is not a member/owner of the channel

    Return Value:
        messages: List of dictionaries, where each dictionary 
                contains types { message_id, u_id, message, time_created }
        start:    same as argument "start"
        end:      "start + 50" or -1, if there are no more messages remaining
    '''
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    all_messages = store["messages"]

    # specified dm doesn't exist
    if dm_id not in dms.keys(): 
        raise InputError("Invalid dm_id")

    # declaring default values for return variables
    total_message_num = 0
    messages = []
    end = start + 50

    # if it reaches this point, the dm_id must be valid
    dm_info = dms[dm_id]
    dm_members = dm_info["members"]
    dm_messages = dm_info["messages"]

    # list of message_id's
    total_message_num = len(dm_messages)

    if auth_user_id not in dm_members:
        raise AccessError("Valid dm_id and authorised user not a member")

    # start is greater than the total number of messages in dm
    if start > total_message_num:
        raise InputError("start is an invalid value")

    # Reverse channel_messages so that most recent msg is index 0
    # Then, slice list to get msgs between start and end index
    dm_messages = list(reversed(dm_messages))[start:end]
    messages = [all_messages[x] for x in dm_messages]

   # Add info about if the caller user has reacted to each message in the list of messages
    add_user_react_info(auth_user_id, messages)

    # this is when you return the least recent message in the channel
    # since "start" starts from 0, we use >= rather than > 
    if (start + 50) >= total_message_num:
        end = -1

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Send a message from the authorised user to the dm specified by dm_id
    at a timestamp given by the user.

    Arguments:
        token       (str): the given token
        dm_id       (int): the given dm id
        message     (str): message text
        time_sent   (int): time at which message is to be sent

    Exceptions:
        InputError:
            - dm_id invalid (doesn't exist)
            - length of message is greater than 1000 characters
            - if user is trying to send a message in the past
        AccessError:
            - auth_user_id is invalid (doesn't exist)
            - dm_id is valid and the auth_user_id refers to a user
            who is not a member of the dm

    Return Value:
        message_id  (int): newly created message's id
    '''
    # get auth_user_id from token 
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    message_id_tracker = store["message_id_tracker"]

    # specified dm doesn't exist
    if dm_id not in dms.keys(): 
        raise InputError("Invalid dm_id")

    #if given user is not in dm
    dm_members = dms[dm_id]["members"]
    if auth_user_id not in dm_members:
        raise AccessError("User not a member of the dm")

    if len(message) > 1000:
        raise InputError("Invalid message length")

    #get timestamp of the current time
    curr_timestamp = get_curr_timestamp()

    #if the given stamp is in the past
    if time_sent - curr_timestamp < 0:
        raise InputError (description = "Message is sent in the past")

    react = {
        "react_id" : 1,
        "u_ids" : []
    }

    new_message = {
        "message_id":   message_id_tracker,
        "u_id":         auth_user_id,
        "message":      message,
        "time_created": time_sent,
        "reacts":       [react],
        "is_pinned":    False
    }

    #use the threading library to delay the message
    delay = time_sent - curr_timestamp
    t =threading.Timer(delay, dm_later_helper,[dm_id, auth_user_id, new_message])
    t.start()
    
    return {
        "message_id": message_id_tracker
    }

def dm_later_helper(dm_id, auth_user_id, new_message):
    '''
    Store the message in data store after a delay by threading function

    Arguments:
        dm_id       (int): the given dm id
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
    dms = store["dms"]
    
    #add the new message to the data store
    all_messages = dms[dm_id]["messages"]
    all_messages.append(message_id_tracker)
    store["messages"][message_id_tracker] = new_message

    # send notifications to tagged users
    notifications_send_tagged(auth_user_id, new_message["message"], dm_id, "dm")

    store["message_id_tracker"] = message_id_tracker + 1

    # Update user_stats and workspace_stats for messages_sent
    update_workspace_stats_messages("add")
    update_user_stats_messages(auth_user_id)

    data_store.set(store)

