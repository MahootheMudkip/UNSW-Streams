from src.data_store import data_store
from src.error import InputError, AccessError

def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):

    # Get user and channel data
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # check whether auth_user_id exists
    if auth_user_id not in users.keys():
        raise AccessError("Invalid auth_user_id")

    # check length of channel name is valid
    if not 1 <= len(name) <= 20:
        raise InputError("Invalid channel name")

    # Create new channel and initialise fields
    new_channel = {
        "channel_name": name, 
        "is_public": is_public,
        "owner_members": [auth_user_id],
        "all_members": [auth_user_id],
    }

    # Generate new channel_id
    channel_id = len(channels)

    # Store changes back into database
    channels[channel_id] = new_channel
    store["channels"] = channels
    data_store.set(store)

    return {
        'channel_id': channel_id,
    }
