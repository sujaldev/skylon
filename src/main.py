import os
import pickle
from time import sleep

import chrome  # not to be confused with google chrome


def is_first_launch():
    return not os.path.isfile("user.cache")


def get_user_data():
    if not is_first_launch():
        cache_file = open("user.cache", "rb")
        user_data = pickle.load(cache_file)
        cache_file.close()
        return user_data
    else:
        return ["John", "Doe", "johndoe@example.com", "chromium"]


def launch():
    if is_first_launch():
        chrome.WelcomeLauncher()
        sleep(10)
        launch()
    else:
        user_data = get_user_data()
        engine_preference = user_data[-1]
        if engine_preference == "chromium":
            chrome.launch_chromium()
        else:
            raise NotImplementedError


launch()
