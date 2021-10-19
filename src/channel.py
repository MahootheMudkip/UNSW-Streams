from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id


def channel_invite_v1(token, channel_id, u_id):
    '''
    Invites user and inmmediatly adds them to the channel. 
    Any user inside a channel can invite (owners or members).
    
    Parameters:
        token        (str): the hashed user_id of the invitee.
        channel_id   (int): the given channel id
        u_id         (int): the user_id of the person being invited.
    
    Exceptions:
        InputError:
            - channel_id does not refer to a valid channel.
            - u_id does not refer to a valid user.
            - u_id refers to a user who is already a member of the channel.
        AccessError:
            - The authorised user (auth_user_id) is not a member of the channel.
                - This is also for an invalid auth_user_id
    
    
    Return Type:
    Empty dictionary.
    '''
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    
    # checks for invalid channel_id.
    if channel_id not in channels.keys():
        raise InputError("Invalid Channel. Doesn't exist.")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_all_members = channel_info["all_members"]

    # checks if auth_user is not a member of the channel.
    if auth_user_id not in channel_all_members:
        raise AccessError("Authorised User is not a member of the channel.")
    
    # checks for invalid u_id.
    if u_id not in users.keys():
        raise InputError("Invalid User. Doesn't exist.")
    
    # checks if u_id is already in the channel.
    if u_id in channel_all_members:
        raise InputError("Invited user is already a member of the channel.")

    # If this point is reached, there must be a valid auth_user_id, channel_id and u_id.
    channel_all_members.append(u_id)
    data_store.set(store)

    return {}


def channel_details_v1(token, channel_id):
    '''
    Provides basic details about the channel_id that the auth_user_id is a member of.

    Parameters:
        auth_user_id (int): the given authorised user id.
        channel_id   (int): the given channel id

    Exceptions:
        InputError:
            - Invalid channel_id (doesn't exist) and auth_user_id is valid and a member of the channel.
        AccessError:
            - Authorised user is not member of the channel.
            - Authorised user id is invalid (doesn't exist).

    Return Type:
        name           (str): channel name.
        is_public     (bool): True if channel is public, false otherwise.
        owner_members (list): List of members who own the channel.
        all_members   (list): List of all members including owners.
    '''
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # checks if channel_id exists.
    if channel_id not in channels.keys():
        raise InputError("Invalid Channel id. Channel doesn't exists")

    # Obtain channel information.
    channel_info = channels[channel_id]
    channel_name = channel_info["channel_name"]
    channel_is_public = channel_info["is_public"]

    # list of u_ids
    channel_all_members = channel_info["all_members"]
    
    # test if user is a member of the channel
    if auth_user_id not in channel_all_members:
        raise AccessError("User is not a member of the channel.")
    
    # Creates a list of dictionaries, where each dictionary contains types of user.
    channel_new_all_members = []
    for u_id in channel_all_members:
        new_user = {}
        new_user["u_id"] = u_id
        # users[u_id] is a dictionary of one user.
        # e.g key = "name", value = "Juan"
        for key, value in users[u_id].items():
            if key != "password":
                new_user[key] = value
        channel_new_all_members.append(new_user)
        # appending new_user dictionary
    
    # list of member u_ids
    channel_owner_members = channel_info["owner_members"]
    # Creates a list of dictionaries, where each dictionary contains types of user.
    channel_new_owner_members = []
    for u_id in channel_owner_members:
        new_user = {}
        new_user["u_id"] = u_id
        # users[u_id] is a dictionary of one user.
        # e.g key = "name", value = "Juan"
        for key, value in users[u_id].items():
            if key != "password":
                new_user[key] = value
        channel_new_owner_members.append(new_user)
        # appending new_user dictionary

    return {
        "name": channel_name,
        "is_public": channel_is_public,
        "owner_members": channel_new_owner_members,
        "all_members": channel_new_all_members,
    }

'''
Returns up to 50 messages between index "start" and "start + 50". 
Message with index 0 is the most recent message in the channel. 
This function returns a new index "end" which is the value of "start + 50" or
-1 if there are no more messages to load after this return.

Arguments:
    auth_user_id (int): the given authorised user id
    channel_id   (int): the given channel id
    start        (int): index to start returning messages from
                        (start is assumed to be >= 0)
Exceptions:
    InputError:
        - channel_id invalid (doesn't exist)
        - start > total number of messages in channel
    AccessError:
        - auth_user_id is invalid (doesn't exist)
        - channel_id is valid and the auth_user_id refers to a user
          who is not a member/owner of the channel

Return Value:
    messages: List of dictionaries, where each dictionary 
              contains types { message_id, u_id, message, time_created }
    start:    same as argument "start"
    end:      "start + 50" or -1, if there are no more messages remaining
'''
def channel_messages_v1(auth_user_id, channel_id, start):
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # total_message_num is assumed to be 0 for iteration 1, 
    # as messages has no framework  or implementation
    total_message_num = 0
    messages = []
    end = start + 50

    # check whether auth_user_id exists
    if auth_user_id not in users.keys():  
        raise AccessError("Invalid auth_user_id")

    # specified channel doesn't exist
    if channel_id not in channels.keys(): 
        raise InputError("Invalid channel_id")

    # if it reaches this point, the channel_id must be valid
    channel_info = channels[channel_id]
    channel_members = channel_info["all_members"]

    if auth_user_id not in channel_members:
        raise AccessError("Valid channel_id and authorised user not a member")

    # start is greater than the total number of messages in channel
    if start > total_message_num:
        raise InputError("start is an invalid value")

    # this is when you return the least recent message in the channel
    # since "start" starts from 0, we use >= rather than > 
    if (start + 50) >= total_message_num:
        end = -1

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }

'''
Adds the specified auth_user_id to the given channel_id

Arguments:
    auth_user_id (int): the given authorised user id
    channel_id   (int): the given channel id

Exceptions:
    InputError:
        - channel_id invalid (doesn't exist)
        - auth_user_id already member of channel
    AccessError:
        - auth_user_id is invalid (doesn't exist)
        - channel_id refers to private channel 
          and auth_user_id is not the owner of the channel

Return Value:
    no values returned
'''
def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    if auth_user_id not in users.keys():
        # check whether auth_user_id exists
        raise AccessError("Invalid auth_user_id")
    
    if channel_id not in channels.keys():
        # check whether channel_id exists
        raise InputError("Invalid channel_id")
    
    channel_info = channels[channel_id]
    channel_is_public = channel_info["is_public"]
    channel_members = channel_info["all_members"]
    # channel owners are also included in the "all_members list"
    
    if channel_is_public == False:
        # private channel
        if auth_user_id not in channel_members and users[auth_user_id]["is_owner"] == False:
            # auth_user_id does not refer to a channel member and is 
            # not a global owner
            raise AccessError("Channel is private and authorised user is not an owner/channel member")

    if auth_user_id in channel_members:
        # this checks if the auth_user_id is already a member
        raise InputError("Authorised user already a member of channel")

    # if it reaches this point, auth_user_id and channel_id are both valid
    channel_members.append(auth_user_id)
    data_store.set(store)

    return {}

def channel_leave_v1(token, channel_id):
    '''
    Removes the specified auth_user_id from the given channel_id.

    Arguments:
        token        (str): the hashed authorised user id
        channel_id   (int): the given channel id

    Exceptions:
        InputError:
            - channel_id invalid (doesn't exist)
        AccessError:
            - auth_user_id is invalid (doesn't exist)
            - channel_id is valid but the authorised user 
                is not a member of the channel.

    Return Value:
        no values returned
    '''
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    
    # checks for invalid channel_id.
    if channel_id not in channels.keys():
        raise InputError("Invalid Channel. Doesn't exist.")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_all_members = channel_info["all_members"]
    channel_owners = channel_info["owner_members"]

    # checks if auth_user is not a member of the channel.
    if auth_user_id not in channel_all_members:
        raise AccessError("Authorised User is not a member of the channel.")
    
    if users[auth_user_id]["is_owner"] == True:
        channel_owners.remove(auth_user_id)

    channel_all_members.remove(auth_user_id)
    data_store.set(store)

    return {}