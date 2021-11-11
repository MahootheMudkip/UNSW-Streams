from src import standup
from src.sessions import get_auth_user_id
from src.data_store import data_store
from src.error import InputError, AccessError
from src.stats import *

def channels_list_v1(token):
    '''
    Provides a list of all channels a user is part of.

    Parameters:
        auth_user_id (int): The user id of the person whose public channels are to be displayed

    Exceptions:
        AccessError:
            - When auth_user_id is invalid

    Return Type:
        A list of dictionaries each of which contains the channel_id and name of that channel
    '''
    # get data from data_store
    auth_user_id = get_auth_user_id(token)
    
    store = data_store.get()
    channels = store["channels"]

    # List of channels to be returned
    return_list = []

    # go through each channel's dict
    for channel_id, channel in channels.items():
        # go through all members of every channel dict
        for member_id in channel["all_members"]:
            #if auth user id present in current channel
            if member_id == auth_user_id:
                channel_details = {
                    "channel_id" : channel_id,
                    "name" : channel["channel_name"]
                }
                return_list.append(channel_details)

    return {
        "channels" : return_list
    }

def channels_listall_v1(token):
    '''
    Provides a list of all channels ever created

    Parameters:
        auth_user_id (int)

    Exceptions:
        AccessError:
            - When auth_user_id is invalid

    Return Type:
        A list of dictionaries each of which contains the channel_id and name of that channel
    '''

    # get data from data_store
    get_auth_user_id(token)

    store = data_store.get()
    channels = store["channels"]

    # List of channels to be returned
    return_list = []

    # go through each channel's dict
    for channel_id, channel in channels.items():
        channel_details = {
            "channel_id" : channel_id,
            "name" : channel["channel_name"]
        }
        return_list.append(channel_details)

    return {
        "channels" : return_list
    }

def channels_create_v1(token, name, is_public):
    '''
    Creates a new channel with the given name that is either a public 
    or private channel. 

    Parameters:
        token       (int): the user_id of the channel creator
        name        (str): name of channel to be created
        is_public   (bool): if the channel will be public or private 

    Exceptions:
        InputError:
            - length of name is less than 1 or more than 20 characters
        AccessError:
            - auth_user_id is invalid (doesn't exist)

    Return Type:
        channel_id: id of channel that has been created
    '''

    # Get user and channel data
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    channels = store["channels"]

    # check length of channel name is valid
    if not 1 <= len(name) <= 20:
        raise InputError(description="Invalid channel name")

    standup = {
        "is_active": False,
        "message_queue": [],
        "time_finish": 0
    }
    
    # Create new channel and initialise fields
    new_channel = {
        "channel_name": name,
        "is_public": is_public,
        "owner_members": [auth_user_id],
        "all_members": [auth_user_id],
        "messages": [],
        "standup": standup
    }

    # Generate new channel_id
    channel_id = len(channels)

    # Store changes back into database
    channels[channel_id] = new_channel

    # Update user_stats and workplace_stats
    update_workplace_stats_channels()
    update_user_stats_channels(auth_user_id, "add")

    data_store.set(store)

    return {
        'channel_id': channel_id,
    }
