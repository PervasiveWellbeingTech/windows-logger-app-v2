# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 15:51:32 2020

@author: Hugo
"""

import csv
import datetime

#computer_name = "DESKTOP-SGGRUD3"
#survey_data = None
#csv_header = None
#
#with open("MyQualtricsDownload/Moustress test.csv") as csv_file:
#    csv_reader = csv.reader(csv_file, delimiter=",")
#    for index, row in enumerate(csv_reader):
#        if index == 0:
#            csv_header = row
#        if row[-1] == computer_name:
#            survey_data = row
#
#if csv_header is not None:
#    print(csv_header)
#
#if survey_data is not None:
#    print(survey_data)


def get_surveys(computer_name):
    print(f"[INFO] Searching survey answers for {computer_name}...")
    try:
        with open("qualtrics_survey/Moustress test.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            
            answers = []
            for row in csv_reader:
                if row[-1] == computer_name:
                    answers.append(row)
        
        if answers:
            print(f"[INFO] {len(answers)} answers found for {computer_name}")
            return answers
        else:
            print("[WARNING] Not answers found for {computer_name}")
    except:
        print("[ERROR] Survey file not found")


def get_last_survey(computer_name):
    surveys = get_surveys(computer_name)
    
    if surveys:
        # Select only surveys with 100% completion
        surveys = [survey for survey in surveys if survey[4] == "100"]
        
        if surveys:
            # Sort surveys according to the time of completion
            surveys.sort(key=lambda x: x[1])
        
            return surveys[-1]
