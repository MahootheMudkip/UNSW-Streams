from urllib.parse import urlparse, urlunparse
from src.data_store import data_store

def update_port_numbers(port):
    '''
    this updates all the "profile_img_url" to the new port
    to prevent links from breaking when the port changes

    Example:
    old_img_url = 'http://localhost:11112/images/default.jpg'
    new_img_url = 'http://localhost:8080/images/default.jpg'
    '''
    store = data_store.get()
    users = store["users"]

    for user_info in users.values():
        old_img_url = user_info["profile_img_url"]
        new_img_url = urlparse(old_img_url)
        # break old_img_url into components
        new_img_url = new_img_url._replace(netloc=f"localhost:{port}")
        # change the port
        new_img_url = urlunparse(new_img_url)
        # recombine to get new url with update port
        user_info["profile_img_url"] = new_img_url
    
    data_store.set(store)