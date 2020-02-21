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

*put survey process schema here*


## logger

## notification
