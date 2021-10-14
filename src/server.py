import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config

from src.other import clear_v1
from src.auth import *
from src.channels import *
from src.channel import *


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

    token = data["token"]

    return dumps(auth_login_v1(token))

# @APP.route("/auth/logout/v1", methods=['POST'])
# def auth_logout():
#     data = request.get_json()
# 
#     token = data["token"]
# 
#     return dumps(auth_logout_v1(token))

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    data = request.get_json()

    token = data["token"]
    name = data["name"]
    is_public = data["is_public"]

    return dumps(channels_create_v1(token, name, is_public))

@APP.route("/channels/list/v2", methods=["GET"])
def channels_list():
    data = request.get_json()     

    token = data["token"]
    
    return dumps(channels_list_v1(token))

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    data = request.get_json()

    token = data["token"]

    return dumps(channels_listall_v1(token))

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    data = request.get_json()

    token = data["token"]
    channel_id = data["channel_id"]

    return (dumps(channel_details_v1(token, channel_id)))

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
def channel_invite():
    data = request.get_json()
    token = data["token"]
    channel_id = data["channel_id"]
    start = data["start"]

    return dumps(channel_messages_v1(token, channel_id, start))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
