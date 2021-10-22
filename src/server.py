import sys
import signal
from json import dumps, loads
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config

from src.other import clear_v1
from src.auth import *
from src.channels import *
from src.channel import *
from src.message import *
from src.user import *
from src.dm import *


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/clear/v1", methods=['DELETE'])
def clearv1():
    clear_v1()
    return dumps({})

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    data = request.get_json()

    email = data["email"]
    password = data["password"]
    name_first = data["name_first"]
    name_last = data["name_last"]
    
    return dumps(auth_register_v1(email, password, name_first, name_last))

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    return dumps(auth_login_v1(email, password))

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    data = request.get_json()

    token = data["token"]

    return dumps(auth_logout_v1(token))

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    data = request.get_json()

    token = data["token"]
    name = data["name"]
    is_public = data["is_public"]

    return dumps(channels_create_v1(token, name, is_public))

@APP.route("/channels/list/v2", methods=["GET"])
def channels_list():
    token = request.args.get("token")
    
    return dumps(channels_list_v1(token))

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    token = request.args.get("token")

    return dumps(channels_listall_v1(token))

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    token = request.args.get("token")
    channel_id = request.args.get("channel_id")

    return (dumps(channel_details_v1(token, int(channel_id))))

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    data = request.get_json()
    
    token = data["token"]
    channel_id = data["channel_id"]

    return dumps(channel_join_v1(token, channel_id))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    data = request.get_json()

    token = data["token"]
    channel_id = data["channel_id"]
    u_id = data["u_id"]

    return dumps(channel_invite_v1(token, channel_id, u_id))

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))
    
    return dumps(channel_messages_v1(token, channel_id, start))

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]

    return dumps(channel_leave_v1(token, channel_id))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    u_id = data["u_id"]

    return dumps(channel_addowner_v1(token, channel_id, u_id))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    u_id = data["u_id"]
    
    return dumps(channel_removeowner_v1(token, channel_id, u_id))

@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    data = request.get_json()

    token = data["token"]
    channel_id = data["channel_id"]
    message = data["message"]

    return dumps(message_send_v1(token, channel_id, message))

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()

    token = data["token"]
    message_id = data["message_id"]
    message = data["message"]

    return dumps(message_edit_v1(token, message_id, message))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()
    
    token = data["token"]
    message_id = data["message_id"]

    return dumps(message_remove_v1(token, message_id))

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()

    token = data["token"]
    u_ids = data["u_ids"]

    return dumps(dm_create_v1(token, u_ids))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get("token")
 
    return dumps(dm_list_v1(token))

# @APP.route("/dm/remove/v1", methods=['DELETE'])
# def dm_remove():
#     data = request.get_json()
# 
#     token = data["token"]
#     dm_id = data["dm_id"]
# 
#     return dumps(dm_remove_v1(token, dm_id))

# @APP.route("/dm/details/v1", methods=['GET'])
# def dm_details():
#     token = request.args.get("token")
#     dm_id = request.args.get("dm_id")
# 
#     return dumps(dm_details_v1(token, dm_id))

# @APP.route("/dm/leave/v1", methods=['POST'])
# def dm_leave():
#     data = request.get_json()
# 
#     token = data["token"]
#     dm_id = data["dm_id"]
# 
#     return dumps(dm_leave_v1(token, dm_id))

# @APP.route("/dm/messages/v1", methods=['GET'])
# def dm_messages():
#     token = request.args.gets("token")
#     dm_id = request.args.get("dm_id")
#     start = request.args.get("start")
# 
#     return dumps(dm_messages_v1(token, dm_id, start))

# @APP.route("/message/senddm/v1", methods=['POST'])
# def message_senddm():
#     data = request.get_json()
# 
#     token = data["token"]
#     dm_id = data["dm_id"]
#     message = data["message"]
# 
#     return dumps(message_senddm_v1(tokem, dm_id, message))

@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get("token")

    return dumps(users_all_v1(token))

@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    token = request.args.get("token")
    u_id = int(request.args.get("u_id"))

    return dumps(user_profile_v1(token, u_id))

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    data = request.get_json()

    token = data["token"]
    name_first = data["name_first"]
    name_last = data["name_last"]

    return dumps(user_profile_setname_v1(token, name_first, name_last))

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail():
     data = request.get_json()

     token = data["token"]
     email = data["email"]

     return dumps(user_profile_setemail_v1(token, email))

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    token = data["token"]
    handle_str = data["handle_str"]

    return dumps(user_profile_sethandle_v1(token, handle_str))

# @APP.route("/admin/user/remove/v1", methods=['DELETE'])
# def admin_user_remove():
#     data = request.get_json()
# 
#     token = data["token"]
#     u_id = data["u_id"]
#     
#     return dumps(admin_user_remove_v1(token, u_id))

# @APP.route("/admin/userpermission/change/v1", methods=['POST'])
# def admin_userpermission_change():
#     data = request.get_json()
# 
#     token = data["token"]
#     u_id = data["u_id"]
#     permission_id = data["permission_id"]
# 
#     return dumps(admin_userpermission_change_v1(token, u_id, permission_id))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
