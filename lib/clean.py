import os
import shutil

dirs = [
    "../src/chrome/webrtc_event_logs",
    "../src/chrome/blob_storage",
    "../src/chrome/VideoDecodeStats"
    "../src/webrtc_event_logs",
    "../src/blob_storage",
    "../src/VideoDecodeStats"
]

files = [
    "../src/chrome/error.log"
    "../src/error.log"
]


def clean_cef():
    for directory in dirs:
        try:
            shutil.rmtree(directory)
        except FileNotFoundError:
            print(f"{directory} does not exist.")

    for file in files:
        try:
            os.remove(file)
        except FileNotFoundError:
            print(f"{file} does not exist.")


if __name__ == "__main__":
    clean_cef()
