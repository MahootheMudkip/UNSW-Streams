import re
from src.data_store import data_store
from src.error import InputError
from src.sessions import get_auth_user_id, get_hash, get_token, generate_new_session_id, get_session_id

def auth_login_v1(email, password):
    '''
    Generates a token associated with a new session on 
    valid email + password combo

    Arguments:
        email (str)     - email of user requesting login
        password (str)  - password of user requesting login

    Exceptions:
        InputError:
            - email entered does not belong to a user
            - password is not correct

    Return Value:
        auth_user_id (int)
        token (str)
    '''
    # Get data of users dict from data_store
    store = data_store.get()
    users = store["users"]

    # Check if email and password combination is registered in users dict
    return_id = None
    for u_id, user in users.items():
        if user["email"] == email and user["password"] == get_hash(password):
            # generate a new token for the user indicating a new session
            return_id = u_id
            session_id = generate_new_session_id()
            token = get_token(u_id, session_id)
            user["sessions"].append(session_id)

    # Raise input error if user cannot be logged in
    if return_id == None:
        raise InputError(description="Email or Password is invalid")

    return {
        'auth_user_id': return_id,
        'token': token
    }

def is_taken(users, handle):
    '''
    Check if handle is already taken by another user

    Arguments:
        users (list)  - list of users in data_store
        handle (str)  - name of handle

    Return Values:
        if handle is taken or not (bool)
    '''

    for user in users.values():
        if user["handle_str"] == handle:
            return True
    return False

def generate_handle(name_first, name_last, users):
    '''
    Generate handle using first and last name

    Arguments:
        name_first (str)    - user's first name
        name_last (str)     - user's last name
        users (list)        - list of users in data_store

    Return Values:
        handle (str)
    ''' 
    # - initial handle generated from concatenation of lowercase-only alphanumeric first name and last name
    # - cut down to 20 characters
    handle = ""
    for character in name_first + name_last:
        if character.isalnum():
            handle += character.lower()
    handle = handle[:20]

    # If handle is taken, add smallest integer after current handle
    if is_taken(users, handle):
        duplicate_number = 0
        while is_taken(users, handle + str(duplicate_number)):
            duplicate_number += 1
        handle = handle + str(duplicate_number)

    return handle

def auth_register_v1(email, password, name_first, name_last):
    '''
    Create a new account for a user given their details

    Arguments:
        email (str)         - email of user requesting registration
        password (str)      - password of user requesting registration
        name_first (str)    - first name of user requesting registration
        name_last (str)     - last name of user requesting registration

    Exceptions:
        InputError:
            - email entered is not a valid email 
            - email address is already being used by another user
            - length of password is less than 6 characters
            - length of name_first is not between 1 and 50 characters inclusive
            - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        auth_user_id (int)  - user's id in the system
        token (str)         - JWT token indicative of new session
        
    '''

    # Get data of users dict from data_store
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
    if len(password) < 6:
        raise InputError(description="Password must be at least 6 characters")
    if not 1 <= len(name_first) <= 50:
        raise InputError(description="First name must be between 1 and 50 characters long")
    if not 1 <= len(name_last) <= 50:
        raise InputError(description="Last name must be between 1 and 50 characters long")

    # generate handle for user
    handle = generate_handle(name_first, name_last, users)
    # generate u_id for user
    u_id = len(users)
    # start new session and generate token for user
    session_id = generate_new_session_id()
    token = get_token(u_id, session_id)

    # Append dict for new user containing user info
    users[u_id] = {
        "email": email, 
        "name_first": name_first,
        "name_last": name_last,
        "password": get_hash(password),
        "handle_str": handle,
        "is_owner": False,
        "sessions": [session_id]
    }
    # If user is first user to register, they are a global owner
    if u_id == 0:
        users[u_id]["is_owner"] = True

    # Set data containing user information
    data_store.set(store)

    return {
        'auth_user_id': u_id,
        'token': token,
    }

def auth_logout_v1(token):
    '''
    Logout of session associated with given token

    Arguments:
        token (str)         - token to be invalidated

    Exceptions:
        AccessError:
            - token entered is invalid

    Return Values:
        Empty dict
    ''' 
    store = data_store.get()
    users = store["users"]

    # get auth_user_id and session_id from token
    auth_user_id = get_auth_user_id(token)
    session_id = get_session_id(token)

    # remove session_id from sessions list
    sessions = users[auth_user_id]["sessions"]
    sessions.remove(session_id)

    data_store.set(store)

    return {}