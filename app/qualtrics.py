# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 15:23:38 2020

@author: Hugo
"""

# Code from the Qualtrics API documentation:
# https://api.qualtrics.com/docs/getting-survey-responses-via-the-new-export-apis

import requests
import zipfile
import io, os
import sys
import re
from requests.exceptions import HTTPError


def exportSurvey(apiToken,surveyId, dataCenter, fileFormat):
    
    # Setting static parameters
    requestCheckProgress = 0.0
    progressStatus = "inProgress"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
    headers = {
        "content-type": "application/json",
        "x-api-token": apiToken,
    }

    # Step 1: Creating Data Export
    downloadRequestUrl = baseUrl
    downloadRequestPayload = '{"format":"' + fileFormat + '"}'
    
    try:
        downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)

        # If the response was successful, no Exception will be raised
        downloadRequestResponse.raise_for_status()
    except HTTPError as http_err:
        print("[ERROR] HTTP error occurred: {}".format(http_err))
        return None
    except Exception as err:
        print("[ERROR] Unknown error occurred during Qualtrics request: {}".format(err))
        return None
    else:
        print("[INFO] Qualtrics request response received")
        if downloadRequestResponse:
            print("[INFO] Qualtrics response successful - Status code: {}".format(downloadRequestResponse.status_code))
        else:
            print("[ERROR] Qualtrics response unsuccessful - Status code: {}".format(downloadRequestResponse.status_code))
            return None
    
    # Step 2: Checking on Data Export Progress and waiting until export is ready
    try:
        progressId = downloadRequestResponse.json()["result"]["progressId"]
        print("[INFO] Data export in progress...")
        while progressStatus != "complete" and progressStatus != "failed":
            print ("\tprogressStatus=", progressStatus)
            requestCheckUrl = baseUrl + progressId
            requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
            requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
            print("\tDownload is " + str(requestCheckProgress) + " complete")
            progressStatus = requestCheckResponse.json()["result"]["status"]
    except Exception as err:
        print("[ERROR] Error during Qualtrics data export: {}".format(err))
        return None

    #step 2.1: Check for error
    if progressStatus == "failed":
        print("[ERROR] Qualtrics data export failed")
        return None
    else:
        print("\tComplete")

    try:
        fileId = requestCheckResponse.json()["result"]["fileId"]
        # Step 3: Downloading file
        requestDownloadUrl = baseUrl + fileId + '/file'
        requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)
    except Exception as err:
        print("[ERROR] Error during downloading Qualtrics survey file: {}".format(err))
        return None

    try:
        # Step 4: Unzipping the file
        zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall("qualtrics_survey")
    except Exception as err:
        print("[ERROR] Error when unzipping Qualtrics survey file: {}".format(err))
        return None
    
    print("[INFO] Qualtrics survey file correctly downloaded and unzipped")
    return True


def main():
    
    try:
      apiToken = os.environ.get("API_TOKEN")
      dataCenter = os.environ.get("DATA_CENTER")
      surveyId = os.environ.get("SURVEY_ID")
      fileFormat = os.environ.get("FILE_FORMAT")
    except KeyError:
      print("[ERROR] Set environment variables API_TOKEN, DATA_CENTER, SURVEY_ID and FILE_FORMAT")
      sys.exit(2)

    if fileFormat not in ["csv", "tsv", "spss"]:
        print ("[ERROR] fileFormat must be either csv, tsv, or spss")
        sys.exit(2)
 
    r = re.compile('^SV_.*')
    m = r.match(surveyId)
    if not m:
       print ("[ERROR] surveyId must match ^SV_.*")
       sys.exit(2)

    return exportSurvey(apiToken, surveyId,dataCenter, fileFormat)
