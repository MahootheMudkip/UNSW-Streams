from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store["users"] = {}
    store["channels"] = {}
    store["global_owner"] = -1
    data_store.set(store)
