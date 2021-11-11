import re
import requests
import os
from PIL import Image
from os.path import splitext
from urllib.parse import urlparse
from src.error import AccessError, InputError
from src.data_store import data_store
from src.sessions import get_auth_user_id
from src.auth import auth_login_v1, is_taken
from src.config import url
from src.gen_timestamp import get_curr_timestamp


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

    # timestamp for unique url generation
    timestamp = str(get_curr_timestamp())

    # file name to save as
    file_name = f"{auth_user_id}X{timestamp}.jpg"
    new_location = os.path.join(images_dir, file_name)

    # crop file and save
    img.crop((x_start, y_start, x_end, y_end)).save(new_location)
    
    # assigning img url to specified user
    store = data_store.get()
    user_info = store["users"][auth_user_id]
    user_info["profile_img_url"] = url[:-1] + f"/images/{file_name}"
    data_store.set(store)

    return {}

# determine wether the given handle is in a specified channel
def handle_in_channel(handle, channel_id):
    store = data_store.get()
    users = store["users"]
    channel = store["channels"][channel_id]

    for u_id in channel["all_members"]:
        if users[u_id]["handle_str"] == handle:
            return True

# determine wether the given handle is in a specified dm
def handle_in_dm(handle, dm_id):
    store = data_store.get()
    users = store["users"]
    dm = store["dms"][dm_id]

    for u_id in dm["members"]:
        if users[u_id]["handle_str"] == handle:
            return True

def to_uid(handle):
    store = data_store.get()
    users = store["users"]

    for u_id, user in users.items():
        if user["handle_str"] == handle:
            return u_id
            
# find location of message in channel
def find_location(message_id):
    store = data_store.get()
    channels = store["channels"]
    dms = store["dms"]
    
    # Search for location of message in channels
    for ch_id, channel in channels.items():
        if message_id in channel["messages"]:
            return {
                "location_type": "channel",
                "location_id": ch_id
            }

    # If not found, then search for location in dms
    for dm_id, dm in dms.items():
        if message_id in dm["messages"]:
            return {
                "location_type": "dm",
                "location_id": dm_id
            }

# send notifications to users tagged in a message
def notifications_send_tagged(sender_id, message, platform_id, platform_type):
    store = data_store.get()
    users = store["users"]
    sender = users[sender_id]["handle_str"]

    # get list of tagged users using regex
    tagged_users = []
    for i, char in enumerate(message):
        if char == "@":
            rest_of_msg = message[i+1:]
            tagged_user = re.split('[^a-zA-Z\\d]', rest_of_msg)[0]
            tagged_users.append(tagged_user)

    # make list of tagged users unique 
    tagged_users = set(tagged_users)

    # send notifications for tags that are valid
    for handle in tagged_users:
        # tagged message in channel
        if platform_type == "channel":
            # check if handle exists in specified channel
            if handle_in_channel(handle, platform_id):
                channel_name = store["channels"][platform_id]["channel_name"]
                notification = {
                    "channel_id": platform_id,
                    "dm_id": -1,
                    "notification_message": f"{sender} tagged you in {channel_name}: {message[:20]}"
                }
                users[to_uid(handle)]["notifications"].insert(0, notification)
        # tagged message in dm
        else:
            # check if handle exists in specified dm
            if handle_in_dm(handle, platform_id):
                dm_name = store["dms"][platform_id]["name"]
                notification = {
                    "channel_id": -1,
                    "dm_id": platform_id,
                    "notification_message": f"{sender} tagged you in {dm_name}: {message[:20]}"
                }
                users[to_uid(handle)]["notifications"].insert(0, notification)

    # set data_store (users now have new notifications)
    data_store.set(store)

# Send notifications when user's message has been reacted to
def notifications_send_reacted(reactor_id, message_id):
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]

    # get sender and reactor info
    sender = store["messages"][message_id]["u_id"]
    reactor = users[reactor_id]["handle_str"]
    
    # get location of message
    location = find_location(message_id)
    location_type = location["location_type"]
    location_id = location["location_id"]

    # Change fields in notification based on location of message
    if location_type == "channel":
        location_name = channels[location_id]["channel_name"]
        channel_id = location_id
        dm_id = -1
    else:
        location_name = dms[location_id]["name"]
        channel_id = -1
        dm_id = location_id

    # Create notification and send  
    notification = {
        "channel_id": channel_id,
        "dm_id": dm_id,
        "notification_message": f"{reactor} reacted to your message in {location_name}"
    }
    users[sender]["notifications"].insert(0, notification)
        
    # set data_store (user now has new notifications)
    data_store.set(store)

# Send notifications when user is added to a new channel/dm 
def notifications_send_invited(auth_user_id, u_id, location_id, location_type):
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]
    dms = store["dms"]

    # get handle of inviter
    inviter = users[auth_user_id]["handle_str"]
    
    # Change fields in notification based on location of invite
    if location_type == "channel":
        location_name = channels[location_id]["channel_name"]
        channel_id = location_id
        dm_id = -1
    else:
        location_name = dms[location_id]["name"]
        channel_id = -1
        dm_id = location_id

    # Create notification and send  
    notification = {
        "channel_id": channel_id,
        "dm_id": dm_id,
        "notification_message": f"{inviter} added you to {location_name}"
    }
    users[u_id]["notifications"].insert(0, notification)
        
    # set data_store (user now has new notifications)
    data_store.set(store)

def notifications_get_v1(token):
    '''
    Returns user's most recent 20 notifications

    Arguments:
        token  (str): the given token

    Exceptions:
        none 
    Return Value:
        notifications (list of notification dicts)
    '''
    auth_user_id = get_auth_user_id(token)
    store = data_store.get()
    users = store["users"]

    return {
        "notifications": users[auth_user_id]["notifications"][:20]
    }
