# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:23:05 2020

@author: Hugo
"""

import os
import time
import datetime


def find_last_file(folder_path):
    """Used to find the most recently modified file in the given folder."""
    
    last_modification_timestamp = 0
    last_modified_file_name = None
    
    for file_name in os.listdir(folder_path):
        modification_timestamp = os.path.getmtime(folder_path + file_name)
        if modification_timestamp > last_modification_timestamp:
            last_modification_timestamp = modification_timestamp
            last_modified_file_name = file_name
    
    return last_modified_file_name


def is_last_modification_recent(file_name, folder_path, time_threshold):
    """
    Returns True if the last modification (of the given file in the given folder)
    occurred recently, according to the given time_threshold.
    If the last modification occurred more than time_threshold-seconds ago,
    the function returns False
    """
    
    modification_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(folder_path + file_name))
    modification_timestamp = modification_time.timestamp()
    current_timestamp = datetime.datetime.utcnow().timestamp()

    return current_timestamp - modification_timestamp < time_threshold


def wait_user():
    """
    Sleeps while the user is not here.
    To determine if the user is here, we check whether the mouse moves or not.
    To know if the mouse is moving, we use the log files made by the mouse logger.
    The idea is to look when the last movement occurred.
    To do that:
        - we find the most recently modified log file in the DATA_STORAGE folder
        - we check whether the last modification of this file occurred recently
        
    The sleep time between each verification is defined by the TIME_BEFORE_AVAILABILITY_CHECK
    variable (which is in seconds).
    This variable is used to reduce the processing because we do not need to check
    constantly if the user is here or not (a human is moving at seconds-scale, instead
    of the milliseconds-scale of the computer)
    """
    
    print("[INFO] Waiting for user availability...")
    
    DATA_STORAGE_PATH = os.environ.get("DATA_STORAGE_PATH")
    # Time to wait between each iteration of the process (in seconds)
    TIME_BEFORE_AVAILABILITY_CHECK = int(os.environ.get("TIME_BEFORE_AVAILABILITY_CHECK"))
    
    file_name = find_last_file(DATA_STORAGE_PATH)
    
    while not (file_name and is_last_modification_recent(file_name, DATA_STORAGE_PATH, TIME_BEFORE_AVAILABILITY_CHECK)):
        time.sleep(TIME_BEFORE_AVAILABILITY_CHECK)
        file_name = find_last_file(DATA_STORAGE_PATH)
    
    print("[INFO] User available")
        