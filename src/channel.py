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

    if auth_user_id not in users.keys():
        # check whether auth_user_id exists
        raise AccessError("invalid auth_user_id")
    
    channels = store["channels"]
    if channel_id not in channels.keys():
        raise InputError("invalid channel_id")
    
    channel_info = channels[channel_id]
    channel_members = channel_info["all_members"]
    channel_owners = channel_info["owner_members"]
    channel_is_public = channel_info["is_public"]

    if channel_is_public == False:
        # private channel
        if auth_user_id not in channel_owners:
            # auth_user_id does not refer to a channel owner
            raise AccessError("channel is private and authorised user is not an owner")
        # else:
        #     raise InputError("authorised user is an owner and already a member of channel")
    else:
        # public channel
        if auth_user_id in channel_members or auth_user_id in channel_owners:
            raise InputError("authorised user already a member of channel")

    # if it reaches this point, auth_user_id and channel_id are both valid
    channel_members.append(auth_user_id)
    data_store.set(store)

    return {}
