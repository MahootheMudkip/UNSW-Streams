from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.auth import is_taken
import re
from src.auth import is_taken

'''
Returns a list of all users and their associated details.

Arguments:
    token  (str): the given token

Exceptions:
    AccessError:
        - invalid token

Return Value:
    users  (list of dicts): list of dict `users`
'''
def users_all_v1(token):
    # this functions will handle all exceptions for tokens
    get_auth_user_id(token)
    
    store = data_store.get()
    users = store["users"]
    users_list = []

    for u_id, user_info in users.items():
        # add user to list if they're not a removed user
        if user_info["email"] != None and user_info["handle_str"] != None:
            user_copy = user_info.copy()
            # creates a separate dict copy
            user_copy.pop("password")
            user_copy.pop("is_owner")
            user_copy.pop("sessions")
            # remove password item from dict
            user_copy["u_id"] = u_id
            users_list.append(user_copy)
        
    return {
        "users": users_list
    }

def user_profile_v1(token, u_id):
    # this functions will handle all exceptions for tokens
    get_auth_user_id(token)
    
    store = data_store.get()
    users = store["users"]
    
    # u_id not a key in users dictionary
    if u_id not in users.keys():
        raise InputError(description="u_id does not refer to a valid user")

    # make a copy of the specified u_id's dictionary
    user_info = users[u_id]
    user_copy = user_info.copy()
    # remove unecessary fields
    user_copy.pop("password")
    user_copy.pop("is_owner")
    user_copy.pop("sessions")
    # add u_id item
    user_copy["u_id"] = u_id

    return {
        "user": user_copy
    }

def user_profile_setname_v1(token, name_first, name_last):
    '''
    Sets user's first name and last name to a new name

    Arguments:
        token  (str): the given token
        name_first (str): the first name given
        name_last (str): the last name given

    Exceptions:
        AccessError:
            - invalid token

        InputError:
            - first name or last name is < 1 character or > 51 characters

    Return Value:
        empty dictionary
    '''
    # get user_id
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    user = store["users"][auth_user_id]
    
    # First name and last name are a valid amount of characters
    if not 1 <= len(name_first) <= 50:
        raise InputError(description="First name must be between 1 and 50 characters long")
    if not 1 <= len(name_last) <= 50:
        raise InputError(description="Last name must be between 1 and 50 characters long")

    # change first name and last name
    user["name_first"] = name_first
    user["name_last"] = name_last

    data_store.set(store)
    return {}

def user_profile_setemail_v1(token, email):
    '''
    Sets user's email to a new email

    Arguments:
        token  (str): the given token
        email  (str): the given email

    Exceptions:
        AccessError:
            - invalid token

        InputError:
            - email entered is not a valid email.
            - email is already taken.

    Return Value:
        empty dictionary
    '''
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]

    # Perform series of checks to make sure registration can be authorised
    # - Email entered is not a valid email (does not match regex)
    if re.fullmatch(R'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email) == None:
        raise InputError(description="Invalid email format")
    # - Email address is already being used by another user
    for user in users.values():
        if user["email"] == email:
            raise InputError(description="Email already taken")

    user = store["users"][auth_user_id]
    user["email"] = email
    data_store.set(store)

    return {}

def user_profile_sethandle_v1(token, handle_str):
    '''
    Sets user's handle_str to a new handle.

    Arguments:
        token  (str): the given token
        handle (str): the given handle

    Exceptions:
        AccessError:
            - invalid token

        InputError:
            - length of handle_str is not between 3 and 20 characters inclusive
            - handle_str contains characters that are not alphanumeric
            - the handle is already used by another user

    Return Value:
        empty dictionary
    '''
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]
    user = store["users"][auth_user_id]
    
    handle_length = len(handle_str)

    if handle_length < 3 or handle_length > 20:
        raise InputError(description="Handle must be between 3 and 20 characters inclusive.")
    
    if handle_str.isalnum() == False:
        raise InputError(description="Handle must only contain alphanumeric characters.")

    if is_taken(users, handle_str) == True:
        raise InputError(description="Handle is already taken.")
    
    # Update user handle
    user["handle_str"] = handle_str
    data_store.set(store)

    return {}
