import re
import requests
import os
from PIL import Image
from os.path import splitext
from urllib.parse import urlparse
from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.auth import is_taken
from src.auth import is_taken
from src.config import url

NO_ERROR = 200

def users_all_v1(token):
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
            user_copy.pop("notifications")
            user_copy.pop("user_stats")
            # remove password item from dict
            user_copy["u_id"] = u_id
            users_list.append(user_copy)
        
    return {
        "users": users_list
    }

def user_profile_v1(token, u_id):
    '''
    For a valid user, returns information about their user_id, 
    email, first name, last name, and handle

    Arguments:
        token  (str): the given token
        u_id   (int): the user_id which we want to get the information of

    Exceptions:
        AccessError:
            - invalid token
        InputError:
            - u_id does not refer to a valid user

    Return Value:
        user  (dict): of type `user`
    '''
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
    user_copy.pop("notifications")
    user_copy.pop("user_stats")
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

# NOTE: through testing, the cwd when this function is called is from the root
# directory, "/tmp_amd/cage/export/cage/5/z5363771/1531/ass1/project-backend"
# hence we need to save the file in the images directory
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of an image on the internet, crops the image 
    within bounds (x_start, y_start) and (x_end, y_end). 
    Position (0,0) is the top left. 

    Arguments:
        token   (str): the given token
        img_url (str): the url of the image to download
        x_start (int): dimensions to crop image to 
        y_start (int): dimensions to crop image to 
        x_end   (int): dimensions to crop image to
        y_en    (int): dimensions to crop image to

    Exceptions:
        AccessError:
            - invalid token

        InputError:
            - http status other than 200 returned
            = any of x_start, y_start, x_end, y_end are not 
              within the dimensions of the image at the URL
            - x_end is less than x_start or y_end is less than y_start
            - image uploaded is not a JPG

    Return Value:
        n/a
    '''
    auth_user_id = get_auth_user_id(token)

    # testing size params valid
    if x_start < 0 or y_start < 0:
        raise InputError(description="cannot have negative x and y values")
    if x_end <= x_start or y_end <= y_start:
        raise InputError(description="x and y param values")
    
    # getting url path from img_url
    # we need to separate path from params, which will affect os.path.splitext
    url_path = urlparse(img_url).path
    file_ext = splitext(url_path)[1]
    # testing file type
    if file_ext != ".jpg":
        raise InputError(description="img_url does not link to a JPG image")

    # downloading file from url
    try:
        response = requests.get(img_url)
    except requests.exceptions.ConnectionError as e:
        # had to change this to keep pylint happy
        raise InputError(description="connection error") from e
        
    if response.status_code != NO_ERROR:
        # error occured
        raise InputError(description="status code returned not 200")
    with open("temp.jpg", "wb") as FILE:
        FILE.write(response.content)

    # now we should modify the file
    img = Image.open("temp.jpg")
    # get img dimensions
    width, height = img.size

    # check x and y values are with img dimensions
    if width < x_start or width < x_end:
        raise InputError(description="x params greater than img")
    elif height < y_start or height < y_end:
        raise InputError(description="y params greater than img")

    # get current working dir location
    cwd = os.getcwd()
    # generate images dir location
    images_dir = os.path.join(cwd, "images")
    # generate new file location
    new_location = os.path.join(images_dir, f"{auth_user_id}.jpg")

    # crop file and save
    img.crop((x_start, y_start, x_end, y_end)).save(new_location)
    
    # assigning img url to specified user
    store = data_store.get()
    user_info = store["users"][auth_user_id]
    user_info["profile_img_url"] = url[:-1] + f"/images/{auth_user_id}.jpg"
    data_store.set(store)

    return {}

    
    
