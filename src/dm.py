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