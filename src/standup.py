from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from datetime import *
import time, threading

def standup_start_v1(token, channel_id, length):
    
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    channels = store["channels"]
    
    if channel_id not in channels.keys():
        # check whether channel_id exists
        raise InputError(description="Invalid channel_id")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_all_members = channel_info["all_members"]

    # checks if auth_user is not a member of the channel.
    if auth_user_id not in channel_all_members:
        raise AccessError(description="Authorised User is not a member of the channel.")

    if length < 0:
        raise InputError(description="length must be a positive integer")

    standup = store["channels"][channel_id]["standup"]
    if standup["is_active"] == True:
        raise InputError(description="Standup already active in this channel")

    
    standup["is_active"] = True
    curr_timestamp = datetime.now().replace(tzinfo=timezone.utc).timestamp()

    time_finish = int(curr_timestamp + length)
    standup = store["channels"][channel_id]["standup"]
    standup["time_finish"] = time_finish
    
    # thread to end standup once time_finish is reached
    thread = threading.Thread(target=end_standup,args=(channel_id, length,))
    thread.start()

    data_store.set(store)

    return { 
        "time_finish": time_finish 
        }

def end_standup(channel_id, length):
    
    time.sleep(length)
    store = data_store.get()
    standup = store["channels"][channel_id]["standup"]
    standup["is_active"] = False
    data_store.set(store)