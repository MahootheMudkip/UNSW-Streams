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

    if auth_user_id not in users.keys():
        # check whether auth_user_id exists
        raise AccessError("invalid auth_user_id")

    channels = store["channels"]
    if channel_id not in channels.keys():
        # specified channel doesn't exist
        raise InputError("invalid channel_id")

    # if it reaches this point, the channel_id must be valid
    channel_info = channels[channel_id]
    channel_members = channel_info["all_members"]
    channel_owners = channel_info["owner_members"]

    if auth_user_id not in channel_members and auth_user_id not in channel_owners:
        raise AccessError("channel_id valid and authorised user not member of channel")

    return {
        'messages': [],
        'start': start,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    return {
    }
