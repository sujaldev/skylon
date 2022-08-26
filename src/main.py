import os
import pickle

import chrome  # not to be confused with Google Chrome
from skylon import Skylon


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
    else:
        # user_data = get_user_data()
        # engine_preference = user_data[-1]
        engine_preference = input("Enter engine preference (skylon(s)/chromium(c)): ").lower()
        if engine_preference in ("chromium", "c"):
            chrome.launch_chromium()
        elif engine_preference in ("skylon", "s"):
            Skylon("Skylon Browser", 1000, 800).start_event_loop()
        else:
            print("Wrong engine choice, try again")
            launch()


launch()
