# Stanford Pervasive Wellbeing Tech Lab (PWTL) - Windows mouse logger application (v2)

"app" is the main application. "logger" and "notification" are the source code of two sub-applications used in the main application.

**How to launch the app ?**

*Works for Windows only (tested on Windows 10)*

- Download the "app" folder
- Verify that the **conf_prod.txt** file contains one key,value pair per line (and not everything on the same line, cf. below for details)
- Launch the **main** file. Three options to launch this file:
  - Run **main.py** directly in an IDE
  - Run the command line `%python% main.py` (where `%python%` is your python path)
  - Run the command line `cmd /K main.exe` to run the compiled code

## app

The PWT Lab wants to use the information on how you interact with a computer mouse to build models to estimate stress. The purpose of this application is to record mouse movements of the user. Periodically, it will also display a survey to the user which may include few questions, like how stress you are on a scale of 1-10.

### Global architecture

![Global Architecture](https://github.com/PervasiveWellbeingTech/windows-logger-app-v2/blob/master/img/architecture.png)

The role of each element of this architecture is explained below.

### Workflow

To run the application, launch the **main.py** file.

- the user ID is retrieved first, and then it checks from the Users whitelist stored on the network share if the user is part of the study or not. 
- if the user is not part of the study, the program ends (if the user is not part of the study, then we do not want to record their mouse movements)
- if the user is part of the study, then the mouse logger **logger.exe** is launched. From that moment, all mouse movements are stored in a file on the network drive in a user specific sub directory
- a survey is periodically displayed (see below for detailed explanation on this process)

To stop the mouse logger application, launch the **logout.py** file.

### Survey

A survey is periodically displayed to the user. It is used to provide labels to go along with the mouse data.  
The user has the choice to answer or not to the survey. We want to track the survey answers to modify the time between two surveys.  
For example, we display a survey: if the user answers this survey, we will display the next survey in 4 hours (example). But if the 
user ignores the survey, we will display the next survey in 30 minutes.  
The survey is build and shared through Qualtrics.

There are basically three steps leading to displaying a survey:
- checking the need to display the survey
- checking the presence of the user (the user may not be in front of the screen)
- displaying the survey (this itself can be done in 2 ways)

#### Checking the need to display the survey

There are three cases:
- if the user never answered the survey, we move on to the next step (checking the presence of the user)
- if the user answered the survey a long time ago (say > 4 hours ago as an example), we move on to the next step (checking the presence of the user)
- if the user answered the survey recently (say < 4 hours ago as an example), we wait and recheck after a set time as per 'TIME_BEFORE_NEW_CHECK' variable in the conf_prod (or any variant of this file)

Now, to know if the user already answered a survey or when he answered it the last time, we use the [Qualtrics API](https://api.qualtrics.com/docs).   
We call the Qualtrics API to get a list of all the answered surveys (the code for the call is in the **qualtrics.py** file
and the list of the answered surveys is stored in the "qualtrics_survey" folder). Then we do basic parsing to determine when the current
user last filled out the survey (code in the **survey_analyzer.py** file).

#### Checking the presence of the user

If we assume that the user is present when he/she uses his/her mouse, then we can detect if he/she is actually here or not because we are recording all the mouse movements (with the **logger.exe** application).  
So we just have to look for the most recent mouse data file and check if it has been modified recently (code in the **log_file_controller.py** file). If it is the case, we move on to the next step (displaying the survey if the previous step on checking the need to display the survery found that we have to display the survey), else we wait for the user to move the mouse.

#### Displaying the survey

This can be done in two different ways:
- directly display the survey in a web browser
- display a windows notification that will open a web page with the survey, only if it is clicked
In both cases, the user can choose to not answer the survey in closing the web page.

If we want to use the notification way, we launch the **notification.exe** windows application that will display it.  
The choice between these two options is done using the configuration file (cf. below).

The URL of the web page is dynamically built to include the user ID so that we know who answered a survey without having to directly ask for their identity to users.

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

The configuration file used by default is **conf_prod.txt**. But you can create as many configuration files as you want.  
The name of the file must respect the format: "conf_" + name + ".txt". For example, you can add a **conf_custom.txt** file to the
app folder.

Then, to use this configuration file instead of the default one, you can launch the **main.py** file in adding a parameter (command line):
```
python main.py custom
```
(where `python` is the python path on your system)

## logger

This application records all mouse movements (only, no keyboard logging).
More precisely:
- x and y motions of the mouse
- x and y coordinates of the cursor (screen)
- mouse wheel state (if there is a wheel)

### Code

The application is a simple Windows App that uses the Win32 API to have a direct access to hardware.
All the code is contained in one C++ file **Main.cpp**.
Developed with Microsoft Visual Studio 2019.

#### How a Windows application works ? (roughly speaking)

A Windows application needs two essential components: a window (yay) and procedure.

The window is used to receive all messages (events, for example when the user clicks on a button) from Windows.
This window is represented by the `WinMain` function in the code.

When the window receives a message, it transmits the message to the procedure.
The procedure contains the process to follow for each message (event) we want to handle.
The procedure is represented by the `WndProc` function, which contains a list (switch-case) of all the events we are interested in.

#### How this application works ?

##### Window
This application runs as a service (it is invisible).
So the window should be invisible. To do that we can use a "Message-only window" whose name is pretty explicit: it is used only to receive messages and can not be used to interact with it (it is invisible actually).

To setup this kind of window we just have to specify `HWND_MESSAGE` as a parameter of the `CreateWindow` function (in `WinMain`).

##### Procedure
The procedure handles three messages:
- `WM_CREATE`
- `WM_DESTROY`
- `WM_INPUT`

`WM_CREATE` is received when the window is created. We create file for writing data in it and we specify which data we want to get from the Raw Input interface. To specify that we use the two following lines:
```
rid.usUsagePage = 1;
rid.usUsage = 2;
```
(`rid` for "Raw Input Device")

`rid.usUsagePage = 1` means that we want to register generic desktop controls
In this category "generic desktop controls" we can choose more precisely what we want with `usUsage`.
`rid.usUsage = 2` means that we want mouse data (6 is used to get keyboard data for example).

`WM_DESTROY` is received when the window is destroyed.

`WM_INPUT` is the core message of the application. It is received every time we have a new device input (mouse movement for example).
Here is how we get data:
```
raw->data.mouse.usButtonFlags,
raw->data.mouse.usButtonData,
raw->data.mouse.lLastX,
raw->data.mouse.lLastY,
```

`usButtonFlags` contains an hexadecimal number that corresponds to the mouse state, see the "RAWINPUT (mouse)" link at the bottom to interpret this number.  
`usButtonData` contains the mouse wheel "value" when the mouse wheel is used (cf. "Mouse wheel" link at the bottom for more information on this value).  
`lLastX` and `lLastY` represent x and y motions of the mouse  
(cf. RAWINPUT links for more details)

To get the cursor position on the screen we also use the `GetCursorPos` function.

Another thing we do when we receive a `WM_INPUT` message is to check the time.
Indeed, we change the storage file every hour of inactivity, which means that if the mouse is not used for one hour, we will create a new file to store data. It avoids us having all the data in a single file and allows us to divide them into kind of "user sessions".

Lines are stored in this format: `timestamp,usButtonFlags,usButtonData,lLastX,lLastY,cursorX,cursorY` (timestamp in milliseconds).


#### Links that helped me to build this application
Win32 app documentation: https://docs.microsoft.com/en-us/windows/win32/  
Window app with Visual Studio: https://docs.microsoft.com/en-us/cpp/windows/walkthrough-creating-windows-desktop-applications-cpp?view=vs-2019  

Detailed explanation for a keylogger app: https://www.codeproject.com/Articles/297312/Minimal-Key-Logger-using-RAWINPUT  

RAWINPUT: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawinput?redirectedfrom=MSDN  
RAWINPUT (mouse): https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawmouse  
Mouse wheel: https://docs.microsoft.com/en-us/windows/win32/learnwin32/other-mouse-operations#mouse-wheel
GetCursorPos: https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursorpos?redirectedfrom=MSDN  

## notification

Same code structure than the logger application.  
We use a library to display notifications: https://github.com/mohabouje/WinToast
