# Stanford Pervasive Wellbeing Tech Lab (PWTL) - Windows mouse logger application (v2)

"app" is the main application. "logger" and "notification" are the source code of two sub-applications used in the main application.

## app

The PWT Lab wants to study mouse movements. The purpose of this application is to record mouse movements of the user. Periodically, it will also display a survey to the user.

### Global architecture

![Global Architecture](https://github.com/PervasiveWellbeingTech/windows-logger-app-v2/blob/master/img/architecture.png)

The role of each element of this architecture is explained below.

### Workflow

To run the application, launch the **main.py** file.

- the user ID is retrieved first
- if the user is not part of the study, the program ends (some workstation users could not be enrolled in the Stanford study. In this case we do not want to record their movements)
- the mouse logger **logger.exe** is launched. From that moment, all mouse movements are stored in a file
- a survey is periodically displayed (see below for detailed explanation on this process)

To stop the mouse logger application, launch the **logout.py** file.

### Survey

A survey is periodically displayed to the user. It is used to labelised the mouse data.  
The user has the choice to answer or not to the survey. We want to track the survey answers to modify the time between two surveys.  
For example, we display a survey: if the user answers this survey, we will display the next survey in 4 hours (example). But if the 
user ignores the survey, we will display the next survey in 30 minutes.  
The survey is build and shared with Qualtrics.

There are basically three steps to display a survey:
- checking the need to display the survey
- checking the presence of the user (the user may not be in front of his screen)
- displaying the survey

#### Checking the need to display the survey

There are three cases:
- if the user never answered the survey, we move on to the next step
- if the user answered the survey a long time ago, we move on to the next step
- if the user answered the survey recently, we wait

Now, to know if the user already answered a survey or when he answered it the last time, we use the Qualtrics API.  
We call the Qualtrics API to get a list of all the answered surveys (the code for the call is in the **qualtrics.py** file
and the list of the answered surveys is stored in the "qualtrics_survey" folder).

#### Checking the presence of the user

If we assume that the user is present when he uses his mouse, then we can detect if he is actually here or not because we are
recording all the mouse movements (with the **logger.exe** application).  
So we just have to look for the most recent mouse data file and check if it has been modified recently. If it is the case,
we move on to the next step, else we wait for the user to move the mouse.

#### Displaying the survey

This can be done in two different ways:
- directly display the survey in a web browser
- display a windows notification that will open a web page with the survey, only if it is clicked
In both cases, the user can choose to not answer the survey in closing the web page.

If we want to use the notification way, we launch the **notification.exe** windows application that will display it.  
The choice between these two options is done using the configuration file (cf. below).

### Configuration file

The configuration file is a very important piece of the application. It allows us to change the behavior of the application or to
specify some values without having to directly modify the code.

The configuration file contains one pair name-value, name and value are separated by a comma, per line. It is very important to 
respect this syntax. Any typo can lead to an unexpected behavior of the application.

Variables contained is the configuration file (alphabetical order):
- `API_TOKEN`: token used by the Qualtrics API (this value must be kept secret)
- `DATA_CENTER`: information used by the Qualtrics API
- `DATA_STORAGE_PATH`: path to the folder where the mouse data files are stored (very important to end with "/", like "test_folder/")
- `FILE_FORMAT`: file format of the survey answers received after the Qualtrics API call. At the moment, the only supported format by the application is "csv"
- `LOGGER_APP_NAME`: the name of the mouse logger app **logger.exe**
- `NOTIFICATION`: if it is set to "active", we display the survey with a notification before. Else, we display the survey directly
- `NOTIFICATION_APP_NAME`: the name of the notification app **notification.exe**
- `SSL_VERIFICATION`: if it is set to "inactive", the SSL verification will be ignored for the Qualtrics API calls. This should be used only for test purpose and never in production environment.
- `SURVEY_ID`: Qualtrics survey ID
- `SURVEY_NAME`: Qualtrics survey name (case-sensitive)
- `TIME_BEFORE_AVAILABILITY_CHECK`: time (in seconds) before checking again the user's presence (when he is not here)
- `TIME_BEFORE_NEW_CHECK`: time (in seconds) before checking if the user answered the last displayed survey
- `TIME_BEFORE_NEW_SURVEY`: minimum time (in seconds) between two surveys
- `USERNAME_KEY`: this value has to be the name of the environment variable that the program will use to get the user ID (for example, if the user ID is stored in the "USERNAME" environment variable, put "USERNAME_KEY,USERNAME" in the configuration file)
- `USERS_WHITELIST_FILE`: path to the file that contains the users whitelist (example: "folder/users.txt"). Used to know if the user is  part of the study or not

## logger

## notification

## Links

Qualtrics API documentation: https://api.qualtrics.com/docs
