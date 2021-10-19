from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id

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
    # get auth_user_id from token (this function handles all exceptions)
    auth_user_id = get_auth_user_id(token)
    
    store = data_store.get()
    users = store["users"]
    users_list = []

    for u_id, user_info in users.items():
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