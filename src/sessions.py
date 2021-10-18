import hashlib

from flask.globals import session
from src.error import AccessError
import jwt
from src.data_store import data_store

SESSION_TRACKER = 0
SECRET = "8PHk9NI6EuasvQWjvyadYJMB5m4F9W"

def generate_new_session_id():
    """
    Generates a new sequential session ID

    Returns:
        The next session ID (int)
    """
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER


def get_hash(input_string):
    """
    Hashes the input string with sha256

    Args:
        input_string (str)  - The input string to hash

    Returns:
        Encoded string (str)
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


def get_token(auth_user_id, session_id=None):
    """
    Generates a JWT using the global SECRET

    Args:
        auth_user_id (str)  - user_id to be stored in payload

    Returns:
        JWT Encoded string (str) 
    """
    if session_id is None:
        session_id = generate_new_session_id()

    return jwt.encode({'auth_user_id': auth_user_id, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
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
            if jwt_user["session_id"] in users["u_id"]["sessions"]:
                return u_id
    except Exception as e:
        raise AccessError("Token is invalid") from e
    finally:
        raise AccessError("Token is invalid")
