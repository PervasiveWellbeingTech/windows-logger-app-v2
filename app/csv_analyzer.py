# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 15:51:32 2020

@author: Hugo
"""

import csv


def get_surveys(user_name):
    print("[INFO] Searching survey answers for {}...".format(user_name))
    try:
        with open("qualtrics_survey/Moustress test.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            
            answers = []
            for row in csv_reader:
                if row[-1] == user_name:
                    answers.append(row)
        
        if answers:
            print("[INFO] {} answer(s) found for {}".format(len(answers), user_name))
            return answers
        else:
            print("[WARNING] No answer found for {}".format(user_name))
    except Exception as err:
        print("[ERROR] Survey file not found: {}".format(err))


def get_last_survey(user_name):
    surveys = get_surveys(user_name)
    
    try:
        if surveys:
            # Select only surveys with 100% completion
            surveys = [survey for survey in surveys if survey[4] == "100"]
            
            if surveys:
                # Sort surveys according to the time of completion
                surveys.sort(key=lambda x: x[1])
            
                return surveys[-1]
    except Exception as err:
        print("[ERROR] Survey answer parsing error: {}".format(err))
