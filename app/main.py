# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 18:15:33 2020

@author: Hugo
"""

import os
import sys
import time
import datetime
import logging
import random
import win32api
import webbrowser
import qualtrics
import survey_analyzer
import log_file_controller


# General logging configuration
computer_name = os.environ.get("COMPUTERNAME", "unknown_computer_name")
logger = logging.getLogger(computer_name)
logger.setLevel(logging.DEBUG)
logging.Formatter.converter = time.gmtime
line_format = logging.Formatter("%(asctime)s,%(process)d,%(levelname)s,%(message)s",
                               "%Y-%m-%d %H:%M:%S")

# Console logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(line_format)
logger.addHandler(console_handler)

# File logger
file_handler = logging.FileHandler("app_logs/{}.log".format(computer_name), mode="a")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(line_format)
logger.addHandler(file_handler)


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
                elements = line.strip().split(",")
                if len(elements) == 2:
                    key, value = elements
                    os.environ[key] = value
        logger.info("Environment variables setup completed ({} env)".format(env))
        return True
    except Exception as err:  # err is used in logger.exception
        logger.exception("Error during the environment variables setup:")
        return False


def launch_app(app_name):
    """Used to launch a Win32 application, given the application name."""
    
    logger.info("Launching {}...".format(app_name))
    try:
        win32api.WinExec(app_name)
        logger.info("{} launched".format(app_name))
        logger.debug(str([line for line in os.popen("tasklist").readlines() if app_name in line]))
    except:
        logger.error("{} could not be launched properly".format(app_name))


def close_app(app_name):
    """Used to kill a process, given its name"""
    
    logger.info("Closing {}...".format(app_name))
    os.system("taskkill /f /im {}".format(app_name))

    logger.info("{} closed".format(app_name))
    logger.debug(str([line for line in os.popen("tasklist").readlines() if app_name in line]))


def display_survey_time(survey, display_time_mode):
    """
    Given a survey, the function determines how many time (in seconds) we have 
    to wait before displaying the next survey.
    Depending on the display_time_mode, this time is calculated differently.
    The available modes are:
        - random
        - normal (default mode)
        
    Normal (default) mode:
    The time is calculated using the TIME_BEFORE_NEW_SURVEY environment variable.
    Schematically:
        
      given survey       now <---- T ----> next survey
           |________________|_______________|
           <---- TIME_BEFORE_NEW_SURVEY ---->
           
    The function returns T (the time we have to wait before displaying the new survey).
    
    Random mode:
    The time is calculated using TIME_RANDOM_LOWER_BOUND and TIME_RANDOM_UPPER_BOUND
    environment variables.
       
    Instead of having a fixed TIME_BEFORE_NEW_SURVEY value, we compute a random
    value between TIME_RANDOM_LOWER_BOUND and TIME_RANDOM_UPPER_BOUND.
    """
    
    completion_time_survey = survey[1]
    completion_time = datetime.datetime.strptime(completion_time_survey, "%Y-%m-%d %H:%M:%S")
    completion_timestamp = completion_time.timestamp()
    
    current_time = datetime.datetime.utcnow()
    current_timestamp = current_time.timestamp()
    
    logger.info("Display survey time mode: {}".format(display_time_mode))
    if display_time_mode == "random":
        lower_bound = int(os.environ.get("TIME_RANDOM_LOWER_BOUND"))
        upper_bound = int(os.environ.get("TIME_RANDOM_UPPER_BOUND"))
        
        if upper_bound <= lower_bound:
            lower_bound = 0
            upper_bound = 1
            
        time_before_survey = random.randrange(lower_bound, upper_bound)        
    else:
        time_before_survey = int(os.environ.get("TIME_BEFORE_NEW_SURVEY"))
    
    time_from_last_survey = current_timestamp - completion_timestamp
    logger.info("Last survey completed {} seconds ago".format(round(time_from_last_survey)))
    
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
    
    log_file_controller.wait_user(user_name, logger)
    
    if os.environ.get("NOTIFICATION") == "active":
        NOTIFICATION_APP_NAME = os.environ.get("NOTIFICATION_APP_NAME")
        close_app(NOTIFICATION_APP_NAME)
        launch_app(NOTIFICATION_APP_NAME)
    else:
        logger.info("Displaying survey...")
        webbrowser.open(
            "https://stanforduniversity.qualtrics.com/jfe/form/{}?computer_name={}&user_name={}".format(
                survey_id,
                computer_name,
                user_name
            )
        )
        logger.info("Survey displayed")
    

def is_study_user(user_name):
    """Returns True if the given user is in the USERS_WHITELIST file, else False."""
    
    with open(os.environ.get("USERS_WHITELIST_FILE")) as file:
        for user in file.readlines():
            if user.strip() == user_name:
                logger.info("{} is part of the study".format(user_name))
                return True
    
    logger.warning("{} is not part of the study".format(user_name))
    return False


if __name__ == "__main__" and setup_environment_variables():

    close_app(os.environ.get("LOGGER_APP_NAME"))
    
    COMPUTER_NAME = os.environ.get("COMPUTERNAME")
    USER_NAME = os.environ.get(os.environ.get("USERNAME_KEY"))
    
    logger.info("Computer name: {}".format(COMPUTER_NAME))
    logger.info("User name: {}".format(USER_NAME))
    
    # When the current user is not part of the study, we do not launch the logger
    if is_study_user(USER_NAME):
        
        # Launch MouseLogger.exe
        launch_app(os.environ.get("LOGGER_APP_NAME"))
    
        while True:
            logger.info("Process running...")
            
            SURVEY_ID = os.environ.get("SURVEY_ID")
            DISPLAY_TIME_MODE = os.environ.get("DISPLAY_TIME_MODE")
            TIME_BEFORE_NEW_CHECK = int(os.environ.get("TIME_BEFORE_NEW_CHECK"))
            
            # Qualtrics API call to get survey answers
            # (which are stored in the "qualtrics_survey" folder)
            logger.info("Qualtrics API call to retrieve survey answers...")
            if not qualtrics.main(logger):
                logger.warning("Qualtrics API call issue - Process paused (logger still running)")
                logger.info("Waiting time: {} seconds".format(TIME_BEFORE_NEW_CHECK))
                time.sleep(TIME_BEFORE_NEW_CHECK)
            
            # Find the last Qualtrics survey answered by the given user
            last_survey = survey_analyzer.get_last_survey(USER_NAME, logger)
            
            if last_survey:
                # Decide if we should display the survey or not
                # This choice is based on the given time
                waiting_time_before_survey = display_survey_time(last_survey, DISPLAY_TIME_MODE)
                
                if waiting_time_before_survey <= 0:
                    display_survey(SURVEY_ID, COMPUTER_NAME, USER_NAME)
                    sleep_time = TIME_BEFORE_NEW_CHECK
                else:
                    logger.info("The survey does not need to be displayed right now")
                    sleep_time = round(waiting_time_before_survey) + 1
            else:
                display_survey(SURVEY_ID, COMPUTER_NAME, USER_NAME)
                sleep_time = TIME_BEFORE_NEW_CHECK
            
            logger.info("Waiting time: {} seconds".format(sleep_time))
            time.sleep(sleep_time)
