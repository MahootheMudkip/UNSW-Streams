import pytest
import requests
from src.config import url

NO_ERROR = 200
ACCESS_ERROR = 403
INPUT_ERROR = 400
# error status codes

URL = url + "user/profile/uploadphoto/v1" 
# image below is 1920 x 1080
IMG_URL = "http://allpcworld.com/wp-content/uploads/2016/09/Ubuntu-latest-version-free-download.jpg"
PNG_FILE = "http://vignette4.wikia.nocookie.net/pokemon/images/e/e7/129Magikarp_OS_anime.png"
HTTPS_FILE = "https://media.nauticamilanonline.com/product/altavoz-pokeball-pokemon-800x800.jpg"

@pytest.fixture
def initial_setup():
    # clear all stored data
    requests.delete(url + "clear/v1")

    # url route
    auth_register_url = url + "auth/register/v2"

    # create new user 0, (global owner) and extracts token
    user0_response = requests.post(auth_register_url, json={      
        "email":        "theboss@gmail.com", 
        "password":     "999999",
        "name_first":   "Big", 
        "name_last":    "Boss"
    })
    user0 = user0_response.json()
    user0_token = user0["token"]

    # create new user 1 and extract token
    user1_response = requests.post(auth_register_url, json={      
        "email":        "lmao@gmail.com", 
        "password":     "123789",
        "name_first":   "Jeremy", 
        "name_last":    "Clarkson"
    })
    user1 = user1_response.json()
    user1_token = user1["token"]
    user1_id = user1["auth_user_id"]

    return {
        "user0_token":  user0_token,
        "user1_token":  user1_token,
        "user1_id":     user1_id
    }

# invalid token only
def test_invalid_token(initial_setup):
    response = requests.post(URL, json={
        "token":    "fake",
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    400,
        "y_end":    400
    })
    assert response.status_code == ACCESS_ERROR

# x_end < x_start, y_end < y_start
def test_start_end_params(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  400,
        "y_start":  0,
        "x_end":    0,
        "y_end":    400
    })
    assert response.status_code == INPUT_ERROR

    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  400,
        "x_end":    400,
        "y_end":    0
    })
    assert response.status_code == INPUT_ERROR

    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  400,
        "y_start":  400,
        "x_end":    0,
        "y_end":    0
    })
    assert response.status_code == INPUT_ERROR

# all size params are 0
def test_all_size_params_zero(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    0,
        "y_end":    0
    })
    assert response.status_code == NO_ERROR

# image uploaded is not a jpg file
def test_not_jpg_file(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  PNG_FILE,
        "x_start":  0,
        "y_start":  0,
        "x_end":    50,
        "y_end":    50
    })
    assert response.status_code == INPUT_ERROR

# image link given is HTTPS
def test_https_url(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  HTTPS_FILE,
        "x_start":  0,
        "y_start":  0,
        "x_end":    50,
        "y_end":    50
    })
    assert response.status_code == INPUT_ERROR

# given size params are not within the dimensions of the image
def test_size_params_not_within_image(initial_setup):
    user1_token = initial_setup["user1_token"]
    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    2000,
        "y_end":    400
    })
    assert response.status_code == INPUT_ERROR

    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    400,
        "y_end":    5161
    })
    assert response.status_code == INPUT_ERROR

    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  500,
        "y_start":  500,
        "x_end":    2000,
        "y_end":    1000
    })
    assert response.status_code == INPUT_ERROR

# test that users have a default img_url set
def test_https_url(initial_setup):
    user1_token = initial_setup["user1_token"]
    user1_id = initial_setup["user1_id"]

    response = requests.get(f'{url}user/profile/v1', params={
        "token":    user1_token,
        "u_id":     user1_id
    })
    assert response.status_code == NO_ERROR
    assert response.json()["user"]["profile_img_url"] != ""

# test working (have to check img downloads)
def test_working(initial_setup):
    user0_token = initial_setup["user0_token"]
    user1_token = initial_setup["user1_token"]

    response = requests.post(URL, json={
        "token":    user1_token,
        "img_url":  IMG_URL,
        "x_start":  0,
        "y_start":  0,
        "x_end":    100,
        "y_end":    200
    })
    assert response.status_code == NO_ERROR

    response = requests.post(URL, json={
        "token":    user0_token,
        "img_url":  IMG_URL,
        "x_start":  500,
        "y_start":  500,
        "x_end":    1000,
        "y_end":    1000
    })
    assert response.status_code == NO_ERROR
    








