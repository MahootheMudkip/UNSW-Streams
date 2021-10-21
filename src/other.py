from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store["users"] = {}
    store["channels"] = {}
    store["dms"] = {}
    store["messages"] = {}
    store["session_id_tracker"] = 0
    store["dm_id_tracker"] = 0
    store["message_id_tracker"] = 0
    data_store.set(store)
