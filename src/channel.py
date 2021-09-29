from src.error import AccessError, InputError
from src.data_store import data_store


def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

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

def channel_details_v1(auth_user_id, channel_id):
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    
    # checks if auth_user_id exists.
    if auth_user_id not in users.keys():
        raise AccessError("Invalid Authorised User ID. User doesn't exist")

    # checks if channel_id exists.
    if channel_id not in channels.keys():
        raise InputError("Invalid Channel id. Channel doesn't exists")
    
    # Obtain channel information.
    channel_details = channels[channel_id]
    channel_name = channel_details["name"]
    channel_is_public = channel_details["is_public"]
    channel_all_members = channel_details["all_members"]
    channel_owners = channel_details["owner_members"]

    # test if user is a memver of the channel
    if auth_user_id not in channel_all_members:
        raise AccessError("User is not a member of the channel.")
    
    return {
        channel_name,
        channel_is_public,
        channel_owners,
        channel_all_members,
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    return {
    }
