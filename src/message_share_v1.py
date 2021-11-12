from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.user import notifications_send_reacted, notifications_send_tagged
from src.stats import *
from src.gen_timestamp import get_curr_timestamp
from src.dm import message_senddm_v1
from src.message import message_send_v1

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    
    #check for invalid token
    auth_user_id = get_auth_user_id(token)

    #if channel_id and dm are equal to -1 
    if channel_id == -1 and dm_id == -1:
        raise InputError("Both ids are -1")
    #if channel_id and dm_id are valid, raise error
    if channel_id != -1 and dm_id != -1:
        raise InputError("neither channel_id nor dm_id are -1")
   
    #check if channel is valid
    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]

    # specified channel doesn't exist
    if dm_id == -1 and channel_id not in channels.keys(): 
        raise InputError(description="Invalid channel_id")
    # specified dm doesn't exist
    if channel_id == -1 and dm_id not in dms.keys(): 
        raise InputError(description="Invalid dm_id")
    
    
    # sending a message to channel
    if dm_id == -1:
        channel_info = channels[channel_id]
        if auth_user_id not in channel_info["all_members"]:
            raise AccessError(description = "user not member of channel, the message is being sent to")
        
    # sending a message to dm
    if channel_id == -1:
        dm_info = dms[dm_id]
        if auth_user_id not in dm_info["members"]:
            raise AccessError(description = "user not member of dm, the message is being sent to")

    #check if the og message id belongs to a message
    location_found = False
    for channel in channels.values():
        if auth_user_id in channel["all_members"]:
            if og_message_id in channel["messages"]:
                location_found = True
                break
    
    if location_found == False:
        for dm in dms.values():
            if auth_user_id in dm["members"]:
                if og_message_id in dm["messages"]:
                    location_found = True
                    break

    if location_found == False:
        raise InputError(description="message_id not within a channel/dm that the user has joined")

    # get the message from og message id
    messages = store["messages"]
    old_message = messages[og_message_id]["message"]
    new_message = f"{old_message} {message}"

    # check the length of new message
    if len(new_message) > 1000:
        raise InputError(description="length of message greater than 1000 characters")

    # if channel_id given, call message send
    if dm_id == -1:
        return message_send_v1(token, channel_id, new_message)
    else:
        return message_senddm_v1(token, dm_id, new_message)
