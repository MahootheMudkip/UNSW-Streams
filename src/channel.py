from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.message import add_user_react_info
from src.user import notifications_send_invited
from src.stats import *


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
        raise InputError(description="Invalid Channel. Doesn't exist.")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_all_members = channel_info["all_members"]

    # checks if auth_user is not a member of the channel.
    if auth_user_id not in channel_all_members:
        raise AccessError(description="Authorised User is not a member of the channel.")
    
    # checks for invalid u_id.
    if u_id not in users.keys():
        raise InputError(description="Invalid User. Doesn't exist.")
    
    # checks if u_id is already in the channel.
    if u_id in channel_all_members:
        raise InputError(description="Invited user is already a member of the channel.")

    # If this point is reached, there must be a valid auth_user_id, channel_id and u_id.
    notifications_send_invited(auth_user_id, u_id, channel_id, "channel")
    channel_all_members.append(u_id)

    # Update user_stats
    update_user_stats_channels(u_id, "add")

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
        raise InputError(description="Invalid Channel id. Channel doesn't exists")

    # Obtain channel information.
    channel_info = channels[channel_id]
    channel_name = channel_info["channel_name"]
    channel_is_public = channel_info["is_public"]

    # list of u_ids
    channel_all_members = channel_info["all_members"]
    
    # test if user is a member of the channel
    if auth_user_id not in channel_all_members:
        raise AccessError(description="User is not a member of the channel.")
    
    # Creates a list of dictionaries, where each dictionary contains types of user.
    channel_new_all_members = []
    for u_id in channel_all_members:
        # appending new_user dictionary
        user_info = users[u_id]
        user_copy = user_info.copy()
        # remove unecessary fields
        user_copy.pop("password")
        user_copy.pop("is_owner")
        user_copy.pop("sessions")
        user_copy.pop("notifications")
        user_copy.pop("user_stats")
        # add u_id item
        user_copy["u_id"] = u_id

        channel_new_all_members.append(user_copy)

    # list of member u_ids
    channel_owner_members = channel_info["owner_members"]
    # Creates a list of dictionaries, where each dictionary contains types of user.
    channel_new_owner_members = []
    for u_id in channel_owner_members:
        # appending new_user dictionary
        user_info = users[u_id]
        user_copy = user_info.copy()
        # remove unecessary fields
        user_copy.pop("password")
        user_copy.pop("is_owner")
        user_copy.pop("sessions")
        user_copy.pop("notifications")
        user_copy.pop("user_stats")
        # add u_id item
        user_copy["u_id"] = u_id

        channel_new_owner_members.append(user_copy)

    return {
        "name": channel_name,
        "is_public": channel_is_public,
        "owner_members": channel_new_owner_members,
        "all_members": channel_new_all_members,
    }

def channel_messages_v1(token, channel_id, start):
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
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    channels = store["channels"]
    all_messages = store["messages"]

    # specified channel doesn't exist
    if channel_id not in channels.keys(): 
        raise InputError(description="Invalid channel_id")

    # declaring default values for return variables
    total_message_num = 0
    messages = []
    end = start + 50

    # if it reaches this point, the channel_id must be valid
    channel_info = channels[channel_id]
    channel_members = channel_info["all_members"]
    channel_messages = channel_info["messages"]

    # list of message_id's
    total_message_num = len(channel_messages)

    if auth_user_id not in channel_members:
        raise AccessError(description="Valid channel_id and authorised user not a member")

    # start is greater than the total number of messages in channel
    if start > total_message_num:
        raise InputError(description="start is an invalid value")

    # Reverse channel_messages so that most recent msg is index 0
    # Then, slice list to get msgs between start and end index
    channel_messages = list(reversed(channel_messages))[start:end]
    messages = [all_messages[x] for x in channel_messages]

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

def channel_join_v1(token, channel_id):
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
    # gets auth_user_id from token and handles exception raising
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    
    if channel_id not in channels.keys():
        # check whether channel_id exists
        raise InputError(description="Invalid channel_id")
    
    channel_info = channels[channel_id]
    channel_is_public = channel_info["is_public"]
    channel_members = channel_info["all_members"]
    # channel owners are also included in the "all_members list"
    
    if channel_is_public == False:
        # private channel
        if auth_user_id not in channel_members and users[auth_user_id]["is_owner"] == False:
            # auth_user_id does not refer to a channel member and is 
            # not a global owner
            raise AccessError(description="Channel is private and authorised user is not an owner/channel member")

    if auth_user_id in channel_members:
        # this checks if the auth_user_id is already a member
        raise InputError(description="Authorised user already a member of channel")

    # if it reaches this point, auth_user_id and channel_id are both valid
    channel_members.append(auth_user_id)

    # Update user_stats
    update_user_stats_channels(auth_user_id, "add")

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
    channels = store["channels"]
    
    # checks for invalid channel_id.
    if channel_id not in channels.keys():
        raise InputError(description="Invalid Channel. Doesn't exist.")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_all_members = channel_info["all_members"]
    channel_owners = channel_info["owner_members"]

    # checks if auth_user is not a member of the channel.
    if auth_user_id not in channel_all_members:
        raise AccessError(description="Authorised User is not a member of the channel.")
    
    if auth_user_id in channel_owners:
        channel_owners.remove(auth_user_id)

    channel_all_members.remove(auth_user_id)

    # Update user_stats
    update_user_stats_channels(auth_user_id, "remove")

    data_store.set(store)

    return {}

def channel_addowner_v1(token, channel_id, u_id):
    '''
    Adds the specified u_id as an owner to the specified channel from the given channel_id.

    Arguments:
        token        (str): the hashed authorised user id
        channel_id   (int): the given channel id
        u_id        (u_id): the auth_user id to become a new owner

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
    channels = store["channels"]
    users = store["users"]

    # checks for invalid channel_id.
    if channel_id not in channels.keys():
        raise InputError(description="Invalid Channel. Doesn't exist.")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_all_members = channel_info["all_members"]
    channel_owners = channel_info["owner_members"]
    
    # check if auth_user does not have owner permissions.
    if users[auth_user_id]["is_owner"] == True:
        if auth_user_id not in channel_all_members:
            raise AccessError(description="Authorised User does not have owner permissions in the channel.")
    elif auth_user_id not in channel_owners:
        raise AccessError(description="Authorised User does not have owner permissions in the channel.")
        
    # checks for invalid u_id.
    if u_id not in users.keys():
        raise InputError(description="Invalid User. Doesn't exist.")

    # checks if auth_user is not a member of the channel.
    if u_id not in channel_all_members:
        raise InputError(description="User is not a member of the channel.")
    
    # check if u_id is already an owner of the channel.
    if u_id in channel_owners:
        raise InputError(description="User is already an owner of this channel.")
    
    channel_owners.append(u_id)
    data_store.set(store)

    return {}

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    Removes the specified u_id as an owner from the specified channel from the given channel_id.

    Arguments:
        token        (str): the hashed authorised user id
        channel_id   (int): the given channel id
        u_id         (int): the auth_user id to remove from owners

    Exceptions:
        InputError:
            - channel_id invalid (doesn't exist)
            - u_id refers to a user who is currently 
                the only owner of the channel.
            - u_id refers to a user who is not an owner of the channel.
            - u_id does not refer to a valid user
        AccessError:
            - auth_user_id is invalid (doesn't exist)
            - channel_id is valid and the authorised user 
                does not have owner permissions in the channel

    Return Value:
        empty dictionary.
    '''
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    channels = store["channels"]
    users = store["users"]

    # checks for invalid channel_id.
    if channel_id not in channels.keys():
        raise InputError(description="Invalid Channel. Doesn't exist.")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_owners = channel_info["owner_members"]
    channel_all_members = channel_info["all_members"]

    # check if auth_user does not have owner permissions.
    if users[auth_user_id]["is_owner"] == True:
        if auth_user_id not in channel_all_members:
            raise AccessError(description="Authorised User does not have owner permissions in the channel.")
    elif auth_user_id not in channel_owners:
        raise AccessError(description="Authorised User does not have owner permissions in the channel.")
        
    # checks for invalid u_id.
    if u_id not in users.keys():
        raise InputError(description="Invalid User. Doesn't exist.")
    
    # check if u_id is not an owner of the channel.
    if u_id not in channel_owners:
        raise InputError(description="User is not an owner of this channel.")
    
    if len(channel_owners) == 1:
        raise InputError(description="Can't remove the only owner of this channel")
    
    channel_owners.remove(u_id)
    data_store.set(store)

    return {}
