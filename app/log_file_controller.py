# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:23:05 2020

@author: Hugo
"""

import os
import time
import datetime

FOLDER_PATH = "data_raw_input/"
SLEEP_TIME = 5  # Time to wait between each iteration of the process (in seconds)

# TODO: Setup conf.txt file

def find_last_file():
    last_modification_timestamp = 0
    last_modified_file_name = None
    
    for file_name in os.listdir(FOLDER_PATH):
        modification_timestamp = os.path.getmtime(FOLDER_PATH + file_name)
        if modification_timestamp > last_modification_timestamp:
            last_modification_timestamp = modification_timestamp
            last_modified_file_name = file_name
    
    return last_modified_file_name


def is_last_modification_recent(file_name):
    modification_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(FOLDER_PATH + file_name))
    modification_timestamp = modification_time.timestamp()
    current_timestamp = datetime.datetime.utcnow().timestamp()

    if current_timestamp - modification_timestamp < SLEEP_TIME:
        return True
    return False


def wait_user():
    print("[INFO] Waiting for user availability...")
    file_name = find_last_file()
    
    while not (file_name and is_last_modification_recent(file_name)):
        time.sleep(SLEEP_TIME)
        file_name = find_last_file()
    
    print("[INFO] User available...")
        