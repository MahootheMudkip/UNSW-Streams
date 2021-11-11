from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.gen_timestamp import get_curr_timestamp


def get_involvement_rate(auth_user_id):
    '''
    Calculate involvement rate for a user:
    num_channels_joined + num_dms_joined + num_msgs_sent / num_channels + num_dms + num_msgs)

    Arguments:
        auth_user_id  (int): user's involvement rate to be calculated

    Exceptions:
        none 

    Return Value:
        involvement_rate (float)
    '''
    # get user_stats and workspace_stats
    store = data_store.get()
    user_stats = store["users"][auth_user_id]["user_stats"]
    workspace_stats = store["users_stats"]

    # find numerator
    num_channels_joined = user_stats["channels_joined"][-1]["num_channels_joined"]
    num_dms_joined = user_stats["dms_joined"][-1]["num_dms_joined"]
    num_msgs_sent = user_stats["messages_sent"][-1]["num_messages_sent"]
    numerator = num_channels_joined + num_dms_joined + num_msgs_sent
    
    # find denominator
    num_channels = workspace_stats["channels_exist"][-1]["num_channels_exist"]
    num_dms = workspace_stats["dms_exist"][-1]["num_dms_exist"]
    num_messages = workspace_stats["messages_exist"][-1]["num_messages_exist"]
    denominator = num_channels + num_dms + num_messages

    if denominator == 0:
        involvement_rate = 0
    else:
        involvement_rate = numerator/denominator
    
    # involvement rate is capped at 1
    if involvement_rate > 1:
        involvement_rate = 1

    return involvement_rate

def get_utilization_rate():
    '''
    Calculate utilization rate for a user:
    num_users_who_have_joined_at_least_one_channel_or_dm / num_users

    Arguments:
        auth_user_id  (int): user's utilization rate to be calculated

    Exceptions:
        none 

    Return Value:
        utilization_rate (float)
    '''
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]

    active_user_count = 0
    in_a_channel = False

    # search for num_users_who_have_joined_at_least_one_channel_or_dm
    for u_id in users.keys():
        for channel in channels.values():
            if u_id in channel["all_members"]:
                active_user_count += 1
                in_a_channel = True
                break
        if not in_a_channel:
            for dm in dms.values():
                if u_id in dm["members"]:
                    active_user_count += 1
                    break

    # search for total_num_users
    total_user_count = 0
    for user in users.values():
        if user["email"] != None and user["handle_str"] != None:   
            total_user_count += 1

    return active_user_count / total_user_count
    
    
def update_user_stats_channels(auth_user_id, change):
    '''
    Update current amount of channels that user is part of

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
    curr_time = get_curr_timestamp()
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
    # append new data entry for channels joined
    user_stats["channels_joined"].append(channels_joined)

    data_store.set(store)

def update_workplace_stats_channels():
    '''
    Update current amount of channels that exist in Streams

    Arguments:
        none

    Exceptions:
        none 

    Return Value:
        none
    '''
    # get current data for workplace stats
    store = data_store.get()
    workspace_stats = store["users_stats"]

    # get current timestamp and current channels exist
    curr_time = get_curr_timestamp()
    curr_channels_exist = workspace_stats["channels_exist"][-1]["num_channels_exist"]

    # form new data entry
    channels_exist = {
        "num_channels_exist": curr_channels_exist + 1,
        "time_stamp": curr_time
    }
    # append new data entry for channels existing 
    workspace_stats["channels_exist"].append(channels_exist)

    data_store.set(store)

def update_user_stats_dms(auth_user_id, change):
    '''
    Update current amount of dms that a user is in

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

    # get current timestamp and current dms joined
    curr_time = get_curr_timestamp()
    curr_dms_joined = user_stats["dms_joined"][-1]["num_dms_joined"]

    # get new # of dms joined based on type of change
    if change == "add":
        curr_dms_joined += 1
    else:
        curr_dms_joined -= 1
    
    # form new data entry
    dms_joined = {
        "num_dms_joined": curr_dms_joined,
        "time_stamp": curr_time
    }
    # append new data entry for dms joined
    user_stats["dms_joined"].append(dms_joined)

    data_store.set(store)

def update_workspace_stats_dms(change):
    '''
    Update current amount of dms that exist in streams

    Arguments:
        change (str): type of change that should be updated (add or remove)

    Exceptions:
        none 

    Return Value:
        none
    '''
    # get current data for workspace stats
    store = data_store.get()
    workspace_stats = store["users_stats"]

    # get current timestamp and current dms existing
    curr_time = get_curr_timestamp()
    curr_dms_exist = workspace_stats["dms_exist"][-1]["num_dms_exist"]

    # get new # of dms existing based on type of change
    if change == "add":
        curr_dms_exist += 1
    else:
        curr_dms_exist -= 1
    
    # form new data entry
    dms_exist = {
        "num_dms_exist": curr_dms_exist,
        "time_stamp": curr_time
    }
    # append new data entry for dms exist
    workspace_stats["dms_exist"].append(dms_exist)

    data_store.set(store)

def update_user_stats_messages(auth_user_id):
    '''
    Update current amount of messages that a user has sent (can only increase
    even if messages are removed)

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

    # get current timestamp and current messages sent
    curr_time = get_curr_timestamp()
    curr_msgs_sent = user_stats["messages_sent"][-1]["num_messages_sent"]
    
    # form new data entry
    messages_sent = {
        "num_messages_sent": curr_msgs_sent + 1,
        "time_stamp": curr_time
    }
    # append new data entry for messages sent
    user_stats["messages_sent"].append(messages_sent)

    data_store.set(store)

def update_workspace_stats_messages(change):
    '''
    Update current amount of messages that exist in streams

    Arguments:
        change (str): type of change that should be updated (add or remove)

    Exceptions:
        none 

    Return Value:
        none
    '''
    # get current data for workspace stats
    store = data_store.get()
    workspace_stats = store["users_stats"]

    # get current timestamp and current dms existing
    curr_time = get_curr_timestamp()
    curr_msgs_exist = workspace_stats["messages_exist"][-1]["num_messages_exist"]
    
    # get new # of messages existing based on type of change
    if change == "add":
        curr_msgs_exist += 1
    else:
        curr_msgs_exist -= 1

    # form new data entry
    messages_exist = {
        "num_messages_exist": curr_msgs_exist,
        "time_stamp": curr_time
    }
    # append new data entry for messages exist
    workspace_stats["messages_exist"].append(messages_exist)

    data_store.set(store)

def user_stats_v1(token):
    '''
    Get user_stats for a particular user

    Arguments:
        token  (int): user's stats to be retrieved

    Exceptions:
        none 

    Return Value:
        user_stats (dict)
    '''

    auth_user_id = get_auth_user_id(token)

    store = data_store.get()

    user_stats = store["users"][auth_user_id]["user_stats"]
    user_stats["involvement_rate"] = get_involvement_rate(auth_user_id)
    return {
        "user_stats": user_stats
    }

def users_stats_v1(token):
    '''
    Get workspace_stats for Streams

    Arguments:
        token  (int): verify they are valid user of Streams

    Exceptions:
        none 

    Return Value:
        workspace_stats (dict)
    '''
    get_auth_user_id(token)

    store = data_store.get()

    users_stats = store["users_stats"]
    users_stats["utilization_rate"] = get_utilization_rate()
    return {
        "workspace_stats": users_stats
    }
