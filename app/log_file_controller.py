# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:23:05 2020

@author: Hugo
"""

import os
import time
import datetime


def find_last_file(folder_path):
    print("FOLDER PATH", folder_path)
    last_modification_timestamp = 0
    last_modified_file_name = None
    
    for file_name in os.listdir(folder_path):
        modification_timestamp = os.path.getmtime(folder_path + file_name)
        if modification_timestamp > last_modification_timestamp:
            last_modification_timestamp = modification_timestamp
            last_modified_file_name = file_name
    
    return last_modified_file_name


def is_last_modification_recent(file_name, folder_path, time_threshold):
    modification_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(folder_path + file_name))
    modification_timestamp = modification_time.timestamp()
    current_timestamp = datetime.datetime.utcnow().timestamp()

    if current_timestamp - modification_timestamp < time_threshold:
        return True
    return False


def wait_user():
    print("[INFO] Waiting for user availability...")
    
    DATA_STORAGE_PATH = os.environ.get("DATA_STORAGE_PATH")
    # Time to wait between each iteration of the process (in seconds)
    TIME_BEFORE_AVAILABILITY_CHECK = int(os.environ.get("TIME_BEFORE_AVAILABILITY_CHECK"))
    
    file_name = find_last_file(DATA_STORAGE_PATH)
    
    while not (file_name and is_last_modification_recent(file_name, DATA_STORAGE_PATH, TIME_BEFORE_AVAILABILITY_CHECK)):
        time.sleep(TIME_BEFORE_AVAILABILITY_CHECK)
        file_name = find_last_file(DATA_STORAGE_PATH)
    
    print("[INFO] User available")
        