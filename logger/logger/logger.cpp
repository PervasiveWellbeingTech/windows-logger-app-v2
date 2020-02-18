#define _CRT_SECURE_NO_DEPRECATE
#include <windows.h>
#include <windowsx.h>
#include <time.h>
#include <stdio.h>
#include <chrono>
#include <string>

#define INFO_BUFFER_SIZE 32767

using namespace std;

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);

HWND hWnd, hActiveWindow, hPrevWindow;
UINT dwSize;
DWORD fWritten;
WCHAR keyChar;
UINT64 newFilePeriod = 3600000;  // in milliseconds
UINT64 nextFileTimestamp;     // used to determine when we have to create a new log file

INT len;
CHAR pWindowTitle[256] = "";
CHAR activeWindowTitle[256] = "";
CHAR* tmpBuf;
CHAR tmpBufLen = 0;
RAWINPUTDEVICE rid;

POINT cursorPoint;

UINT64 getCurrentTimestamp() {
	return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
}

std::wstring getComputerName() {
	TCHAR infoBuf[INFO_BUFFER_SIZE];
	DWORD bufCharCount = INFO_BUFFER_SIZE;

	GetComputerName(infoBuf, &bufCharCount);  // Get the name of the computer and store it in infoBuf
	return infoBuf;
}

std::wstring getUserName() {
	TCHAR infoBuf[INFO_BUFFER_SIZE];
	DWORD bufCharCount = INFO_BUFFER_SIZE;

	GetUserName(infoBuf, &bufCharCount);  // Get the user name and store it in infoBuf
	return infoBuf;
}

std::wstring getEnvironmentVariable(LPCWSTR variableName) {
	TCHAR infoBuf[INFO_BUFFER_SIZE];
	DWORD bufCharCount = INFO_BUFFER_SIZE;

	GetEnvironmentVariable(variableName, infoBuf, bufCharCount);  // Get the name of the computer and store it in infoBuf
	return infoBuf;
}

int openFile(LPCWSTR fileName, LPCWSTR folderName, HANDLE& hFile) {
	// Open log file for writing
	if (CreateDirectory(folderName, NULL) || ERROR_ALREADY_EXISTS == GetLastError()) {
		hFile = CreateFile(fileName, GENERIC_WRITE, FILE_SHARE_READ, 0, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, 0);
		SetFilePointer(hFile, 0, NULL, FILE_END);  // Set the cursor at the end of the file
	}

	if (hFile == INVALID_HANDLE_VALUE) {
		PostQuitMessage(0);
		return -1;
	}

	return 0;
}

class FileManager {
public:
	std::wstring computerFolderName = L"data_computer/";
	std::wstring rawInputFolderName = getEnvironmentVariable(L"DATA_STORAGE_PATH") + getUserName() + L"/";  //L"data_raw_input/user_name/";
	LPCWSTR computerFileName;
	LPCWSTR rawInputFileName;
	HANDLE computerFile;
	HANDLE rawInputFile;
};

FileManager fileManager;


int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
	nextFileTimestamp = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
	nextFileTimestamp = nextFileTimestamp + newFilePeriod;

	// Setup the "computer" file which contains general information about computer, users, sessions
	std::wstring concattedString = fileManager.computerFolderName + getComputerName() + L".log";
	fileManager.computerFileName = concattedString.c_str();
	openFile(fileManager.computerFileName, fileManager.computerFolderName.c_str(), fileManager.computerFile);

	// Window setup
	MSG msg = { 0 };
	WNDCLASS wc = { 0 };

	wc.lpfnWndProc = WndProc;
	wc.hInstance = hInstance;
	wc.lpszClassName = L"Message-Only Window";

	RegisterClass(&wc);
	hWnd = CreateWindow(wc.lpszClassName, NULL, 0, 0, 0, 0, 0, HWND_MESSAGE, NULL, hInstance, NULL);

	while (GetMessage(&msg, hWnd, 0, 0)) {
		TranslateMessage(&msg);
		DispatchMessage(&msg);
	}
	//return msg.wParam;
	return 0;
}

// WndProc is called when a window message is sent to the handle of the window
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	switch (message) {

	case WM_CREATE: {

		// Log message: timestamp,INFO,connection[computer-name]
		UINT64 startTimestamp = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
		CHAR message[300] = "";
		sprintf(message, "%lld,INFO,connection[%ls][%ls]\r\n", startTimestamp, getComputerName().c_str(), getUserName().c_str());
		WriteFile(fileManager.computerFile, message, strlen(message), &fWritten, 0);

		// Setup the "raw input" file which contains all mouse data
		wchar_t tempBuffer[50];
		wchar_t* currentTimestamp = _i64tow(startTimestamp, tempBuffer, 10);

		std::wstring fileName = currentTimestamp;
		std::wstring concattedStdstr = fileManager.rawInputFolderName + fileName + L"_" + getUserName() + L".log";
		fileManager.rawInputFileName = concattedStdstr.c_str();

		if (openFile(fileManager.rawInputFileName, fileManager.rawInputFolderName.c_str(), fileManager.rawInputFile) == 0) {
			CHAR message[300] = "";
			sprintf(message, "%lld,INFO,raw input file created[%ls]\r\n", getCurrentTimestamp(), fileManager.rawInputFileName);
			WriteFile(fileManager.computerFile, message, strlen(message), &fWritten, 0);
		}

		// Choice of raw data we are interested in
		rid.dwFlags = RIDEV_NOLEGACY | RIDEV_INPUTSINK;
		rid.usUsagePage = 1;
		rid.usUsage = 2;
		rid.hwndTarget = hWnd;
		RegisterRawInputDevices(&rid, 1, sizeof(rid));
		break;
	}// end case WM_CREATE

	case WM_DESTROY: {
		CHAR message[300] = "";
		sprintf(message, "%lld,INFO,disconnection[%ls]\r\n", getCurrentTimestamp(), getComputerName().c_str());
		WriteFile(fileManager.computerFile, message, strlen(message), &fWritten, 0);

		FlushFileBuffers(fileManager.computerFile);
		CloseHandle(fileManager.computerFile);
		FlushFileBuffers(fileManager.rawInputFile);
		CloseHandle(fileManager.rawInputFile);
		PostQuitMessage(0);
		break;
	}// end case WM_DESTROY

	case WM_INPUT: {
		if (GetRawInputData((HRAWINPUT)lParam, RID_INPUT, NULL, &dwSize, sizeof(RAWINPUTHEADER)) == -1) {
			PostQuitMessage(0);
			break;
		}

		LPBYTE lpb = new BYTE[dwSize];
		if (lpb == NULL) {
			PostQuitMessage(0);
			break;
		}

		if (GetRawInputData((HRAWINPUT)lParam, RID_INPUT, lpb, &dwSize, sizeof(RAWINPUTHEADER)) != dwSize) {
			delete[] lpb;
			PostQuitMessage(0);
			break;
		}

		// Check the time to see if we have to create a new file or not,
		// because every newFilePeriod-milliseconds we create a new file (to avoid big files)
		UINT64 currentTimestamp = getCurrentTimestamp();

		if (currentTimestamp > nextFileTimestamp) {
			wchar_t tempBuffer[50];
			wchar_t* currentTimestampStr = _i64tow(currentTimestamp, tempBuffer, 10);

			std::wstring fileName(currentTimestampStr);
			std::wstring concattedStdstr = fileManager.rawInputFolderName + fileName + L"_" + getUserName() + L".log";
			fileManager.rawInputFileName = concattedStdstr.c_str();

			CloseHandle(fileManager.rawInputFile);  // Close the previous raw input file

			// Create the new raw input file
			if (openFile(fileManager.rawInputFileName, fileManager.rawInputFolderName.c_str(), fileManager.rawInputFile) == 0) {
				CHAR message[300] = "";
				sprintf(message, "%lld,INFO,new raw input file created[%ls]\r\n", getCurrentTimestamp(), fileManager.rawInputFileName);
				WriteFile(fileManager.computerFile, message, strlen(message), &fWritten, 0);
			}
		}
		nextFileTimestamp = currentTimestamp + newFilePeriod;

		// Storage of raw data in the "raw input" file
		PRAWINPUT raw = (PRAWINPUT)lpb;
		CHAR wt[300] = "";
		GetCursorPos(&cursorPoint);

		sprintf(wt, "%lld,%04x,%04x,%ld,%ld,%ld,%ld\r\n",
			currentTimestamp,
			raw->data.mouse.usButtonFlags,
			raw->data.mouse.usButtonData,
			raw->data.mouse.lLastX,
			raw->data.mouse.lLastY,
			cursorPoint.x,
			cursorPoint.y);

		WriteFile(fileManager.rawInputFile, wt, strlen(wt), &fWritten, 0);
		delete[] lpb;

		return 0;
	}// end case WM_INPUT

	default:
		return DefWindowProc(hWnd, message, wParam, lParam);
	}// end switch

	return 0;
}// end WndProc