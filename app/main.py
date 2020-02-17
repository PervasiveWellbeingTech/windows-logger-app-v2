# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 18:15:33 2020

@author: Hugo
"""

import os
import time
import datetime
import win32api
import webbrowser
import atexit
import qualtrics
import csv_analyzer
import log_file_controller

LOGGER_APP_NAME = "logger.exe"
SLEEP_TIME = 1800              # Number of seconds between each survey check (in seconds)
TIME_BEFORE_NEW_SURVEY = 7200  # Minimum number of seconds before displaying a new survey (in seconds)

# Remove f-string (only Python 3.6+)


def launch_logger():
    print("[INFO] Launching mouse logger...")
    try:
        win32api.WinExec(LOGGER_APP_NAME)
        print("[INFO] Mouse logger launched")
        print([line for line in os.popen('tasklist').readlines() if LOGGER_APP_NAME in line])
    except:
        print("[ERROR] Mouse logger could not be launched properly")


def close_logger():
    print("[INFO] Closing mouse logger...")
    os.system(f"taskkill /f /im {LOGGER_APP_NAME}")

    print("[INFO] Mouse logger closed")
    print([line for line in os.popen('tasklist').readlines() if LOGGER_APP_NAME in line])


def display_survey_time(survey, time_before_survey):
    completion_time_survey = survey[1]
    completion_time = datetime.datetime.strptime(completion_time_survey, "%Y-%m-%d %H:%M:%S")
    completion_timestamp = completion_time.timestamp()
    
    current_time = datetime.datetime.utcnow()
    current_timestamp = current_time.timestamp()
    
    time_from_last_survey = current_timestamp - completion_timestamp
    print(f"[INFO] Last survey completed {round(time_from_last_survey)} seconds ago")
    
    return time_before_survey - time_from_last_survey


def display_survey(computer_name):
    log_file_controller.wait_user()
    
    print("[INFO] Displaying survey...")
    webbrowser.open(f"https://stanforduniversity.qualtrics.com/jfe/form/SV_23QKD9ueJfXlQrz?computer={computer_name}")
    print("[INFO] Survey displayed")
    

def is_study_user(user_name):
    with open("users.txt") as file:
        for user in file.readlines():
            if user.strip() == user_name:
                print(f"[INFO] {user_name} is part of the study")
                return True
    
    print(f"[WARNING] {user_name} is not part of the study")
    return False


if __name__ == "__main__":
    close_logger()
    
    computer_name = os.environ["COMPUTERNAME"]
    user_name = os.environ["USERNAME"]
    
    print(f"[INFO] Computer name: {computer_name}")
    print(f"[INFO] User name: {user_name}")
    
    # When the current user is not part of the study, we do not launch the logger
    if is_study_user(user_name):
        
        # Launch MouseLogger.exe
        launch_logger()
    
        while True:
            print("[INFO] Process running...")
            
            # Qualtrics API call to get survey answers
            # (which are stored in the "qualtrics_survey" folder)
            print("[INFO] Qualtrics API call to retrieve survey answers...")
            if not qualtrics.main():
                print("[WARNING] Qualtrics API call issue - Process paused (logger still running)")
                print(f"[INFO] Waiting time: {SLEEP_TIME} seconds")
                time.sleep(SLEEP_TIME)
            
            # Find the last Qualtrics survey answered by the given user
            last_survey = csv_analyzer.get_last_survey(computer_name)
            
            if last_survey:
                # Decide if we should display the survey or not
                # This choice is based on the given time
                waiting_time_before_survey = display_survey_time(last_survey, TIME_BEFORE_NEW_SURVEY)
                
                if waiting_time_before_survey <= 0:
                    display_survey(computer_name)
                    sleep_time = SLEEP_TIME
                else:
                    print("[INFO] The survey does not need to be displayed")
                    sleep_time = round(waiting_time_before_survey) + 1
            else:
                display_survey(computer_name)
                sleep_time = SLEEP_TIME
            
            print(f"[INFO] Waiting time: {sleep_time} seconds")
            time.sleep(sleep_time)
            
        # Close MouseLogger.exe
        atexit.register(close_logger)
