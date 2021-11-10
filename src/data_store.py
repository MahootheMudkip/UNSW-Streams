import json
import pickle

'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

'''
- "users" is a dictionary containing dictionaries of "user"s
- "user_id"s are used as keys for the "users" dictionary
- each "user" dictionary contains values such as "email", "name_first", "name_last"
eg.

*user_id is an integer
user_id = {
    "email":            string, 
    "name_first":       string,
    "name_last":        string,
    "password":         string,
    "handle_str":       string,
    "is_owner":         bool,
    "sessions":         list of ints(session_ids),
    "user_stats":       dict of user's stats,
    "profile_img_url":  string,
    "notifications":    list of most recent notifications
}

- "channels" is a dictionary containing dictionaries of "channel"s
- "channel_id"s are used as keys for the "channels" dictionary
- each "channel" dictionary contains values such as "is_public", "owner", "members" 
eg.

*channel_id is an integer
channel_id = {
    "channel_name":     string, 
    "is_public":        boolean,
    "owner_members":    list of ints(user_ids),
    "all_members":      list of ints(user_ids)
    "messages:          list of ints(message_ids)
}

- "dms" is a dictionary containing dictionaries of "dm"s
- "dm_id"s are used as keys for the "dms" dictionary
- each "dm" dictionary contains values such as "name", "owner", "members" 
eg.

*dm_id is an integer
dm_id = {
    "name":     string, 
    "owner":    int,
    "members":  list of ints(user_ids),
    "messages:  list of ints(message_ids)
}

- "messages" is a dictionary containing dictionaries of "message"s
- "message_id"s are used as keys for the "messages" dictionary
- each "message" dictionary contains values such as "u_id", "time_created", "message" 
eg.

*message_id is an integer
message_id = {
    "message_id":   int,
    "u_id":         int, 
    "time_created": int,
    "message":      string,
    "reacts":       dict of lists where each key in the dict is a react_id
    "is_pinned":    bool
}

- "users_stats" is a dictionary containing:

Dictionary of shape {
     channels_exist: [{num_channels_exist, time_stamp}], 
     dms_exist: [{num_dms_exist, time_stamp}], 
     messages_exist: [{num_messages_exist, time_stamp}], 
     utilization_rate 
    }

channel_id = {
    "is_active":    bool,
    "time_finish":  int,
    "messages":     dictionary containing dictionaries of messages
} 
'''

initial_object = {
    "users":                {},
    "channels":             {},
    "dms":                  {},
    "messages":             {},
    "session_id_tracker":   0,
    "dm_id_tracker":        0,
    "message_id_tracker":   0,
    "users_stats":          {}
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

# Modified data_store.set to dump initial_object to json file and have persistence.
class Datastore:
    def __init__(self):
        self.__store = initial_object
   
    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store
        with open('database.p', 'wb') as FILE:
            pickle.dump(self.__store, FILE)

print('Loading Datastore...')

global data_store
data_store = Datastore()

