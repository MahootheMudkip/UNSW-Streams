from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.message import message_send_v1
from src.gen_timestamp import get_curr_timestamp
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

    standup = channels[channel_id]["standup"]
    if standup["is_active"] == True:
        raise InputError(description="Standup already active in this channel")

    
    standup["is_active"] = True
    curr_timestamp = get_curr_timestamp()

    time_finish = int(curr_timestamp + length)
    standup = store["channels"][channel_id]["standup"]
    standup["time_finish"] = time_finish
    
    # thread to end standup once time_finish is reached
    thread = threading.Thread(target=end_standup,args=(token, channel_id, length,))
    thread.start()

    data_store.set(store)

    return { 
        "time_finish": time_finish 
        }

def end_standup(token, channel_id, length):
    
    time.sleep(length)
    store = data_store.get()
    channels = store["channels"]
    standup = channels[channel_id]["standup"]
    standup["is_active"] = False
    message_queue = channels[channel_id]["standup"]["message_queue"]
    standup_message = '\n'.join(message_queue)

    message_send_v1(token, channel_id, standup_message)
    data_store.set(store)

def standup_active_v1(token, channel_id):
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
    
    standup = channels[channel_id]["standup"]

    time_finish_return = None
    if standup["is_active"] == True:
        time_finish_return = standup["time_finish"]
    
    is_active_return = standup["is_active"]
    
    return {
        "is_active":    is_active_return,
        "time_finish":  time_finish_return
        }
    
def standup_send_v1(token, channel_id, message):
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    channels = store["channels"]
    users = store["users"]

    if channel_id not in channels.keys():
        # check whether channel_id exists
        raise InputError(description="Invalid channel_id")
    
    # Obtain required channel information.
    channel_info = channels[channel_id]
    channel_all_members = channel_info["all_members"]

    # checks if auth_user is not a member of the channel.
    if auth_user_id not in channel_all_members:
        raise AccessError(description="Authorised User is not a member of the channel.")

    if not 1 <= len(message) <= 1000:
        raise InputError(description="length of message must be under 1000 characters")

    standup = channels[channel_id]["standup"]
    if standup["is_active"] == False:
        raise InputError(description="No active standup in this channel")

    messaque_queue = channels[channel_id]["standup"]["message_queue"]

    user_name = users[auth_user_id]["handle_str"]

    formatted_message = user_name + ": " + message

    messaque_queue.append(formatted_message)
    
    data_store.set(store)

    return {}
    
