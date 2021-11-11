import hashlib
import jwt
from src.data_store import data_store
from src.error import AccessError

SECRET = "8PHk9NI6EuasvQWjvyadYJMB5m4F9W"

def generate_new_session_id():
    """
    Generates a new sequential session ID

    Returns:
        The next session ID (int)
    """
    store = data_store.get()
    session_id_tracker = store["session_id_tracker"]
    store["session_id_tracker"] += 1
    data_store.set(store)
    return session_id_tracker

def get_hash(input_string):
    """
    Hashes the input string with sha256

    Args:
        input_string (str)  - The input string to hash

    Returns:
        Encoded string (str)
    """
    return hashlib.sha256(input_string.encode()).hexdigest()

def get_token(auth_user_id, session_id):
    """
    Generates a JWT using the global SECRET

    Args:
        auth_user_id (str)  - user_id to be stored in payload

    Returns:
        JWT Encoded string (str) 
    """
    return jwt.encode({'auth_user_id': auth_user_id, 'session_id': session_id}, SECRET, algorithm='HS256')

def get_auth_user_id(encoded_jwt):
    """
    Decodes a JWT string and return auth_user_id if token is valid
    Args:
        encoded_jwt (str)  

    Exceptions:
        AccessError:
            - token is invalid/doesn't match expected format
            - auth_user_id in token is invalid
            - session_id in token is invalid

    Returns:
        auth_user_id (int)
    """
    users = data_store.get()["users"]
    try:
        # decode jwt token
        jwt_user = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
        # return auth_user_id if the user_id and session_id matches data_store
        if jwt_user["auth_user_id"] in users:
            u_id = jwt_user["auth_user_id"]
            if jwt_user["session_id"] in users[u_id]["sessions"]:
                return u_id
    # token is not in valid format
    except Exception as e:
        raise AccessError(description="Token is invalid") from e
    # session_id does not exist
    raise AccessError(description="Session is inactive")

def get_session_id(encoded_jwt):
    """
    Decodes a JWT string and return session_id if token is valid
    Args:
        encoded_jwt (str)  

    Exceptions:
        AccessError:
            - token is invalid/doesn't match expected format
            - auth_user_id in token is invalid
            - session_id in token is invalid

    Returns:
        session_id (int)
    """
    # decode jwt token
    jwt_user = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    # return session_id
    return jwt_user["session_id"]

