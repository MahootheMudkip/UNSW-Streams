from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
 

def dm_create_v1(token, u_ids):
    '''
    Creates a new Dm
    
    Arguments:
        token (str):            the given token
        u_ids (list of ints):   contains the user ids of people to be added in the dm
    
    Exceptions:
        InputError:
            - user_ids invalid (doesn't exist)

        AccessError:
            - token invalid
    
    Return Value:
        dm_id (int) 
    '''
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    users = store["users"]
    dm_id = store["dm_id_tracker"]

    #checking if all the u_ids are valid
    for id in u_ids:
        if id not in users.keys() or id == auth_user_id:
            raise InputError("user id is not valid")
    
    # getting values to be entred in the new dm
    u_ids.append(auth_user_id)
    dm_name = ", ".join(sorted([users[u_id]["handle_str"] for u_id in  u_ids]))

    #create dm
    dms[dm_id] = {
        "name" : dm_name,
        "owner" : auth_user_id,
        "members" : u_ids,
        "messages" : []
    }
 
    # Generate new Dm id and update data store dm id with the new dm_id
    store["dm_id_tracker"] += 1
 
    # Store the new dm back to data store
    data_store.set(store)
 
    return {
        "dm_id" : dm_id
    }
  
def dm_list_v1(token):
    '''
    Returns the list of DMs that the user is a member of.
    
    Arguments:
        token (str):            the given token
        
    Exceptions:
        AccessError:
            - token invalid
    
    Return Value:
        A dictionary with dms as key and value being a list of DMs
        that the user is a member of.
    '''
    auth_user_id = get_auth_user_id(token)
    dm_list = []
    
    #extract data from data store
    store = data_store.get()
    dms = store["dms"]
    
    
    #check if the user is part of a dm
    #append the dm_is to dm list if they are
    for dm in dms.keys():
        if auth_user_id in dms[dm]["members"]:
            dm_list.append({"dm_id" : dm , "name" : dms[dm]["name"]})
    
    return {
        "dms" : dm_list
    }    


def dm_details_v1(token, dm_id ):
    
    #get user id from a token
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    users = store["users"]

    #check if user dm id valid
    if dm_id not in dms:
        raise InputError("dm id not valid")

    #check if the user is part of the dm
    if auth_user_id not in dms[dm_id]["members"]:
        raise AccessError("user is not part of the dm")
    
    #extract details
    name = dms[dm_id]["name"]
    member_ids = dms[dm_id]["members"]
    members = []

    #append each member's details from users to members list
    #remove is_owner, password and sessions field
    for member_id in member_ids:
        user = users[member_id]
        user.pop("password")
        user.pop("is_owner")
        user.pop("sessions")
        user["u_id"] = member_id
        members.append(user)
    
    return {
        "name" : name, 
        "members" : members
    }



def dm_remove_v1(token, dm_id):
    #get user id from a token
    auth_user_id = get_auth_user_id(token)

    store = data_store.get()
    dms = store["dms"]
    
    #check if dm id is valid
    if dm_id not in dms:
        raise InputError("dm id not valid")

    #check if user is the owner
    if auth_user_id != dms[dm_id]["owner"]:
        raise AccessError("user not the owner of the dm")

    #remove the dm
    del dms[dm_id]
    
    data_store.set(store)
    return {}

