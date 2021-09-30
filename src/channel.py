from src.error import AccessError, InputError
from src.data_store import data_store

def channel_invite_v1(auth_user_id, channel_id, u_id):
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

'''
Returns up to 50 messages between index "start" and "start + 50". 
Message with index 0 is the most recent message in the channel. 
This function returns a new index "end" which is the value of "start + 50" or
-1 if there are no more messages to load after this return.

Arguments:
    auth_user_id (int): the given authorised user id
    channel_id   (int): the given channel id
    start        (int): index to start returning messages from

Exceptions:
    InputError:
        - channel_id invalid (doesn't exist)
        - start > total number of messages in channel
    AccessError:
        - auth_user_id is invalid (doesn't exist)
        - channel_id is valid and the auth_user_id refers to a user
          who is not a member (or owner?) of the channel

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

    if auth_user_id not in users.keys():
        # check whether auth_user_id exists
        raise AccessError("invalid auth_user_id")

    if channel_id not in channels.keys():
        # specified channel doesn't exist
        raise InputError("invalid channel_id")

    # if it reaches this point, the channel_id must be valid
    channel_info = channels[channel_id]
    channel_members = channel_info["all_members"]

    if auth_user_id not in channel_members:
        raise AccessError("Valid channel_id and authorised user not a member")

    return {
        'messages': [],
        'start': 0,
        'end': 50,
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
    
    if channel_is_public == False and auth_user_id not in channel_members:
        # channel is private and auth_user_id does not refer to 
        # a channel owner or member
        raise AccessError("Channel is private and authorised user is not an owner/channel member")

    if auth_user_id in channel_members:
        # this checks if the auth_user_id is already a member
        raise InputError("Authorised user already a member of channel")

    # if it reaches this point, auth_user_id and channel_id are both valid
    channel_members.append(auth_user_id)
    data_store.set(store)

    return {}
