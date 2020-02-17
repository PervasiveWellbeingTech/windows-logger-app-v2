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
import qualtrics
import csv_analyzer
import log_file_controller

#LOGGER_APP_NAME = "logger.exe"
#TIME_BEFORE_NEW_CHECK = 1800   # Number of seconds between each survey check (in seconds)
#TIME_BEFORE_NEW_SURVEY = 7200  # Minimum number of seconds before displaying a new survey (in seconds)


# TODO: launch module with parameter (%python% main.py -dev)
# TODO: error handling when analyzing survey answers


def setup_environment_variables(env="PROD"):
    conf_file_name = "conf_prod.txt" if env == "PROD" else "conf_dev.txt"
    
    try:
        with open(conf_file_name) as file:
            for line in file.readlines():
                key, value = line.strip().split(",")
                os.environ[key] = value
        print("[INFO] Environment variables setup completed")
        return True
    except Exception as err:
        print("[ERROR] Error during the environment variables setup: {}".format(err))
        return False


def launch_logger(app_name):
    print("[INFO] Launching mouse logger...")
    try:
        win32api.WinExec(app_name)
        print("[INFO] Mouse logger launched")
        print([line for line in os.popen("tasklist").readlines() if app_name in line])
    except:
        print("[ERROR] Mouse logger could not be launched properly")


def close_logger(app_name):
    print("[INFO] Closing mouse logger...")
    os.system("taskkill /f /im {}".format(app_name))

    print("[INFO] Mouse logger closed")
    print([line for line in os.popen("tasklist").readlines() if app_name in line])


def display_survey_time(survey, time_before_survey):
    completion_time_survey = survey[1]
    completion_time = datetime.datetime.strptime(completion_time_survey, "%Y-%m-%d %H:%M:%S")
    completion_timestamp = completion_time.timestamp()
    
    current_time = datetime.datetime.utcnow()
    current_timestamp = current_time.timestamp()
    
    time_from_last_survey = current_timestamp - completion_timestamp
    print("[INFO] Last survey completed {} seconds ago".format(round(time_from_last_survey)))
    
    return time_before_survey - time_from_last_survey


def display_survey(survey_id, computer_name, user_name):
    log_file_controller.wait_user()
    
    print("[INFO] Displaying survey...")
    webbrowser.open(
        "https://stanforduniversity.qualtrics.com/jfe/form/{}?computer_name={}&user_name={}".format(
            survey_id,
            computer_name,
            user_name
        )
    )
    print("[INFO] Survey displayed")
    

def is_study_user(user_name):
    with open("users.txt") as file:
        for user in file.readlines():
            if user.strip() == user_name:
                print("[INFO] {} is part of the study".format(user_name))
                return True
    
    print("[WARNING] {} is not part of the study".format(user_name))
    return False


if __name__ == "__main__" and setup_environment_variables("DEV"):
    close_logger(os.environ.get("LOGGER_APP_NAME"))
    
    COMPUTER_NAME = os.environ["COMPUTERNAME"]
    USER_NAME = os.environ["USERNAME"]
    SURVEY_ID = os.environ["SURVEY_ID"]
    TIME_BEFORE_NEW_CHECK = int(os.environ.get("TIME_BEFORE_NEW_CHECK"))
    TIME_BEFORE_NEW_SURVEY = int(os.environ.get("TIME_BEFORE_NEW_SURVEY"))
    
    print("[INFO] Computer name: {}".format(COMPUTER_NAME))
    print("[INFO] User name: {}".format(USER_NAME))
    
    # When the current user is not part of the study, we do not launch the logger
    if is_study_user(USER_NAME):
        
        # Launch MouseLogger.exe
        launch_logger(os.environ.get("LOGGER_APP_NAME"))
    
        while True:
            print("[INFO] Process running...")
            
            # Qualtrics API call to get survey answers
            # (which are stored in the "qualtrics_survey" folder)
            print("[INFO] Qualtrics API call to retrieve survey answers...")
            if not qualtrics.main():
                print("[WARNING] Qualtrics API call issue - Process paused (logger still running)")
                print("[INFO] Waiting time: {} seconds".format(TIME_BEFORE_NEW_CHECK))
                time.sleep(TIME_BEFORE_NEW_CHECK)
            
            # Find the last Qualtrics survey answered by the given user
            last_survey = csv_analyzer.get_last_survey(USER_NAME)
            
            if last_survey:
                # Decide if we should display the survey or not
                # This choice is based on the given time
                waiting_time_before_survey = display_survey_time(last_survey, TIME_BEFORE_NEW_SURVEY)
                
                if waiting_time_before_survey <= 0:
                    display_survey(SURVEY_ID, COMPUTER_NAME, USER_NAME)
                    sleep_time = TIME_BEFORE_NEW_CHECK
                else:
                    print("[INFO] The survey does not need to be displayed")
                    sleep_time = round(waiting_time_before_survey) + 1
            else:
                display_survey(SURVEY_ID, COMPUTER_NAME, USER_NAME)
                sleep_time = TIME_BEFORE_NEW_CHECK
            
            print("[INFO] Waiting time: {} seconds".format(sleep_time))
            time.sleep(sleep_time)
