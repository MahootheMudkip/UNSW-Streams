from datetime import *
from src.data_store import data_store
from src.sessions import get_auth_user_id

def get_involvement_rate(auth_user_id):
    return 0

def update_user_stats_channels(auth_user_id, change):
    '''
    Update current amount of channels from user

    Arguments:
        auth_user_id  (int): user's stats to be updated

    Exceptions:
        none 

    Return Value:
        none
    '''
    # get current data for user's stats
    store = data_store.get()
    user_stats = store["users"][auth_user_id]["user_stats"]

    # get current timestamp and current channels joined
    curr_time = int(datetime.now().timestamp())
    curr_channels_joined = user_stats["channels_joined"][-1]["num_channels_joined"]

    # get new # of channels joined based on type of change
    if change == "add":
        curr_channels_joined += 1
    else:
        curr_channels_joined -= 1
    
    # form new data entry
    channels_joined = {
        "num_channels_joined": curr_channels_joined,
        "time_stamp": curr_time
    }
    # append new data entry for channels joined and calculate new involvement_rate
    user_stats["channels_joined"].append(channels_joined)
    user_stats["involvement_rate"] = get_involvement_rate(auth_user_id)

    data_store.set(store)

def user_stats_v1(token):
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()

    user_stats = store["users"][auth_user_id]["user_stats"]
    return {
        "user_stats": user_stats
    }
