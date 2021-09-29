from src.error import AccessError, InputError
from src.data_store import data_store

'''
Invites user and inmmediatly adds them to the channel. 
Any user inside a channel can invite (owners or members).

Parameters:
    auth_user_id (int): the user_id of the invitee.
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
This function doesn't return anything.
'''

def channel_invite_v1(auth_user_id, channel_id, u_id):
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # Checks if auth_user_id is invalid.
    if auth_user_id not in users.keys():
        raise AccessError("Invalid Authorised User. Doesn't exist.")
    
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

    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
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
