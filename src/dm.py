from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from datetime import *

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
 
    # Generate new Dm id and update data store dm id with the new dm_id
    store["dm_id_tracker"] += 1
 
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
        # add u_id item
        user_copy["u_id"] = member_id
    
        members.append(user_copy)
    
    return {
        "name" : name, 
        "members" : members
    }



def dm_remove_v1(token, dm_id):
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

    #remove the dm
    del dms[dm_id]
    
    data_store.set(store)
    return {}


def dm_leave_v1(token, dm_id):
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
    data_store.set(store)

    return {}




def message_senddm_v1(token, dm_id, message):

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
    dt = datetime.now()
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

    new_message = {
        "message_id":   message_id_tracker,
        "u_id":         auth_user_id,
        "message":      message,
        "time_created": timestamp
    }

    # append new message_id to the channel messages list
    dm_messages.append(message_id_tracker)

    messages = store["messages"]
    messages[message_id_tracker] = new_message

    store["message_id_tracker"] = message_id_tracker + 1
    data_store.set(store)

    return {
        "message_id": message_id_tracker
    }


def dm_messages_v1(token, dm_id, start):
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

    # this is when you return the least recent message in the channel
    # since "start" starts from 0, we use >= rather than > 
    if (start + 50) >= total_message_num:
        end = -1

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }
