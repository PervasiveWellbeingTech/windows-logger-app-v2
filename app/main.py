# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 18:15:33 2020

@author: Hugo
"""

import os
import sys
import time
import datetime
import win32api
import webbrowser
import qualtrics
import survey_analyzer
import log_file_controller


def setup_environment_variables():
    """
    Creates environment variables according to a configuration file.
    
    The first step is to determine which configuration file to use.
    All configuration files start by "conf_" and end by ".txt".
    By default we use the "conf_prod.txt" file, but we can specify a particular
    file when we launch the script in adding a parameter a the end of the command:
        %python% main.py custom
    with this line, we will use the "conf_custom.txt" file to setup our
    environment variables.
    
    The second and last step is to parse this configuration file.
    The configuration file must have the following format:
        key_1,value_1
        ...
        key_n,value_n
        
    One key-value pair (separated by a comma) per line.
    This way, each line will define one environment variable.
    
    Then, each environment variable defined here can be used like this:
        os.environ.get("key_1")
    to get "value_1" for example
    """
    
    env = "prod"
    
    if len(sys.argv) > 1:
        env = sys.argv[1].lower()

    conf_file_name = "conf_{}.txt".format(env)
    
    try:
        with open(conf_file_name) as file:
            for line in file.readlines():
                key, value = line.strip().split(",")
                os.environ[key] = value
        print("[INFO] Environment variables setup completed ({} env)".format(env))
        return True
    except Exception as err:
        print("[ERROR] Error during the environment variables setup: {}".format(err))
        return False


def launch_app(app_name):
    """Used to launch a Win32 application, given the application name."""
    
    print("[INFO] Launching {}...".format(app_name))
    try:
        win32api.WinExec(app_name)
        print("[INFO] {} launched".format(app_name))
        print([line for line in os.popen("tasklist").readlines() if app_name in line])
    except:
        print("[ERROR] {} could not be launched properly".format(app_name))


def close_app(app_name):
    """Used to kill a process, given its name"""
    
    print("[INFO] Closing {}...".format(app_name))
    os.system("taskkill /f /im {}".format(app_name))

    print("[INFO] {} closed".format(app_name))
    print([line for line in os.popen("tasklist").readlines() if app_name in line])


def display_survey_time(survey, time_before_survey):
    """
    Given a survey, the function determines how many time (in seconds) we have 
    to wait before displaying the next survey.
    This time is calculated using time_before_survey.
    
    Schematically:
        
      given survey       now <-- T --> next survey
           |______________|_____________|
           <---- time_before_survey ---->
       
    The function returns T (the time we have to wait before displaying the new survey)
    """
    
    completion_time_survey = survey[1]
    completion_time = datetime.datetime.strptime(completion_time_survey, "%Y-%m-%d %H:%M:%S")
    completion_timestamp = completion_time.timestamp()
    
    current_time = datetime.datetime.utcnow()
    current_timestamp = current_time.timestamp()
    
    time_from_last_survey = current_timestamp - completion_timestamp
    print("[INFO] Last survey completed {} seconds ago".format(round(time_from_last_survey)))
    
    return time_before_survey - time_from_last_survey


def display_survey(survey_id, computer_name, user_name):
    """
    This function is called when we want to display the survey.
    Before displaying the survey, we wait until the user is there.
    
    Then we check the NOTIFICATION environment variable:
        - if its value is "active" we launch the notification application
        - else, we display the survey directly in the default browser
    
    The parameters survey_id, computer_name and user_name are used to build the link
    to the survey.
    """
    
    log_file_controller.wait_user()
    
    if os.environ.get("NOTIFICATION") == "active":
        NOTIFICATION_APP_NAME = os.environ.get("NOTIFICATION_APP_NAME")
        close_app(NOTIFICATION_APP_NAME)
        launch_app(NOTIFICATION_APP_NAME)
    else:
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
    """Returns True if the given user is in the USERS_WHITELIST file, else False."""
    
    with open(os.environ.get("USERS_WHITELIST_FILE")) as file:
        for user in file.readlines():
            if user.strip() == user_name:
                print("[INFO] {} is part of the study".format(user_name))
                return True
    
    print("[WARNING] {} is not part of the study".format(user_name))
    return False


if __name__ == "__main__" and setup_environment_variables():
    close_app(os.environ.get("LOGGER_APP_NAME"))
    
    COMPUTER_NAME = os.environ.get("COMPUTERNAME")
    USER_NAME = os.environ.get(os.environ.get("USERNAME_KEY"))
    SURVEY_ID = os.environ.get("SURVEY_ID")
    TIME_BEFORE_NEW_CHECK = int(os.environ.get("TIME_BEFORE_NEW_CHECK"))
    TIME_BEFORE_NEW_SURVEY = int(os.environ.get("TIME_BEFORE_NEW_SURVEY"))
    
    print("[INFO] Computer name: {}".format(COMPUTER_NAME))
    print("[INFO] User name: {}".format(USER_NAME))
    
    # When the current user is not part of the study, we do not launch the logger
    if is_study_user(USER_NAME):
        
        # Launch MouseLogger.exe
        launch_app(os.environ.get("LOGGER_APP_NAME"))
    
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
            last_survey = survey_analyzer.get_last_survey(USER_NAME)
            
            if last_survey:
                # Decide if we should display the survey or not
                # This choice is based on the given time
                waiting_time_before_survey = display_survey_time(last_survey, TIME_BEFORE_NEW_SURVEY)
                
                if waiting_time_before_survey <= 0:
                    display_survey(SURVEY_ID, COMPUTER_NAME, USER_NAME)
                    sleep_time = TIME_BEFORE_NEW_CHECK
                else:
                    print("[INFO] The survey does not need to be displayed right now")
                    sleep_time = round(waiting_time_before_survey) + 1
            else:
                display_survey(SURVEY_ID, COMPUTER_NAME, USER_NAME)
                sleep_time = TIME_BEFORE_NEW_CHECK
            
            print("[INFO] Waiting time: {} seconds".format(sleep_time))
            time.sleep(sleep_time)
