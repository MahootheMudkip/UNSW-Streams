from src.error import AccessError, InputError
from src.data_store import data_store
from src.message import message_edit_v1
from src.sessions import get_auth_user_id

def admin_user_remove_v1(token, u_id):
    '''
    Given a u_id, removes the specified user from the Streams.

    Arguments:
        token       (str): the given token
        u_id        (int): the given u_id

    Exceptions:
        InputError:
            - u_id does not refer to a valid user
            - u_id refers to a user who is the only global owner
        AccessError:
            - the authorised user is not a global owner

    Return Value:
        empty dictionary
    '''

    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]
    messages = store["messages"]

    # check if auth_user does not have owner permissions.
    if users[auth_user_id]["is_owner"] == False:
        raise AccessError("Authorised User is not a global owner.")
    
    # checks for invalid u_id.
    if u_id not in users.keys():
        raise InputError("Invalid User. Doesn't exist.")
    
    # remove user from channels
    for channel_id in channels.keys():
        channel_info = channels[channel_id]
        channel_members = channel_info["all_members"]
        channel_owners = channel_info["owner_members"]
        if u_id in channel_owners:
            channel_owners.remove(u_id)
        elif u_id in channel_members:
            channel_members.remove(u_id)
    
    # remove user from dms
    for dm_id in dms.keys():
        dm_info = dms[dm_id]
        dm_members = dm_info["members"]
        if u_id in dm_members:
            dm_members.remove(u_id)
    
    # Replace user's messages with 'Removed user'
    for message_id in messages.keys():
        message_info = messages[message_id]
        user_id = message_info["u_id"]
        if u_id == user_id:
            message_info["message"] = "Removed user"
    
    # Replace user's first name with 'Removed' and last name with 'user'
    user = store["users"][u_id]
    user["name_first"] = "Removed"
    user["name_last"] = "user"

    # Make handle_str and email reusable

    data_store.set(store)

    return {}