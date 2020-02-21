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

## logger

## notification

## Links

Qualtrics API documentation: https://api.qualtrics.com/docs
