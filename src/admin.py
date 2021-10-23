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
            - invalid token

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
        raise AccessError(description="Authorised User is not a global owner.")
    
    # checks for invalid u_id.
    if u_id not in users.keys():
        raise InputError(description="Invalid User. Doesn't exist.")

    global_owners = []
    for user_id, user_info in users.items():
        if user_info["is_owner"] == True:
            global_owners.append(user_id)
    
    if u_id in global_owners and len(global_owners) == 1:
        raise InputError(description="u_id refers to a user who is the only global owner")


    # remove user from channels
    for channel_info in channels.values():
        channel_members = channel_info["all_members"]
        channel_owners = channel_info["owner_members"]
        if u_id in channel_owners:
            channel_owners.remove(u_id)
        if u_id in channel_members:
            channel_members.remove(u_id)
    
    # remove user from dms
    for dm_info in dms.values():
        dm_members = dm_info["members"]
        dm_owner = dm_info["owner"]
        if u_id in dm_members:
            dm_members.remove(u_id)
        if u_id == dm_owner:
            dm_owner = None
    
    # Replace user's messages with 'Removed user'
    for message_info in messages.values():
        user_id = message_info["u_id"]
        if u_id == user_id:
            message_info["message"] = "Removed user"

    
    # Replace user's first name with 'Removed' and last name with 'user'
    user = store["users"][u_id]
    user["name_first"] = "Removed"
    user["name_last"] = "user"

    # logout of all current sessions
    user["sessions"] = []

    # Make handle_str and email reusable
    user["handle_str"] = None
    user["email"] = None

    data_store.set(store)

    return {}


def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    Given a u_id, changes the specified user's stream permissions.

    Arguments:
        token           (str): the given token
        u_id            (int): the given u_id
        permission_id   (int): type of permission to change into

    Exceptions:
        InputError:
            - u_id does not refer to a valid user
            - u_id refers to a user who is the only global owner
            and they are being demoted to member
        AccessError:
            - the authorised user is not a global owner
            - invalid token

    Return Value:
        empty dictionary
    '''

    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]

    # check if auth_user does not have owner permissions.
    if users[auth_user_id]["is_owner"] == False:
        raise AccessError(description="Authorised User is not a global owner.")
    
    # cheks for invalid permission_id
    if permission_id not in [1, 2]:
        raise InputError(description="Permission_id is invalid")

    # checks for invalid u_id.
    if u_id not in users.keys():
        raise InputError(description="Invalid User. Doesn't exist.")
    
    # get list of global_owners
    global_owners = []
    for user_id, user_info in users.items():
        if user_info["is_owner"] == True:
            global_owners.append(user_id)
    
    # checks for u_id being last user with global permissions
    if u_id in global_owners and len(global_owners) == 1 and permission_id == 2:
        raise InputError(description="u_id refers to a user who is the only global owner")

    # change specified user's permissions
    if permission_id == 1:
        users[u_id]["is_owner"] = True
    else:
        users[u_id]["is_owner"] = False

    data_store.set(store)
    return {}