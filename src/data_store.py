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
    "email": string, 
    "name_first": string,
    "name_last": string,
    "password": string,
    "handle_str": string
}

- "channels" is a dictionary containing dictionaries of "channel"s
- "channel_id"s are used as keys for the users dictionary
- each "channel" dictionary contains values such as "is_public", "owner", "members" 
eg.

*channel_id is an integer
channel_id = {
    "channel_name": string, 
    "is_public": boolean,
    "owner_members": list of ints(user_ids),
    "all_members": list of ints(user_ids),
    "handle_str": string
}
'''
initial_object = {
    "users": {},
    "channels": {}
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

