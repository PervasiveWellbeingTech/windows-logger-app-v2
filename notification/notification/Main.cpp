#define _CRT_SECURE_NO_DEPRECATE
#include <windows.h>
#include <windowsx.h>
#include <time.h>
#include <stdio.h>
#include <chrono>
#include <string>
#include <wintoastlib.h>

#define INFO_BUFFER_SIZE 32767

using namespace std;
using namespace WinToastLib;

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);

HWND hWnd, hActiveWindow, hPrevWindow;
UINT dwSize;
DWORD fWritten;
WCHAR keyChar;


INT len;
CHAR pWindowTitle[256] = "";
CHAR activeWindowTitle[256] = "";
CHAR* tmpBuf;
CHAR tmpBufLen = 0;
RAWINPUTDEVICE rid;


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




class CustomHandler : public IWinToastHandler {
public:

	void toastActivated() const {
		std::wstring surveyLink = L"https://stanforduniversity.qualtrics.com/jfe/form/SV_23QKD9ueJfXlQrz?computer_name=" + getComputerName() + L"&user_name=" + getUserName();
		ShellExecute(NULL, L"open", surveyLink.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
	}

	void toastActivated(int actionIndex) const {
		std::wcout << L"The user clicked on button #" << actionIndex << L" in this toast" << std::endl;
	}

	void toastFailed() const {}

	void toastDismissed(WinToastDismissalReason state) const {
		CHAR message[300] = "";
		switch (state) {
		case UserCanceled:
			break;
		case ApplicationHidden:
			break;
		case TimedOut:
			break;
		default:
			break;
		}
	}
};

CustomHandler* handler = new CustomHandler;
WinToastTemplate templ = WinToastTemplate(WinToastTemplate::ImageAndText02);

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{

	// Setup the toast
	WinToast::instance()->setAppName(L"Stanford PWT Lab");

	// companyName, productName, subProduct, versionInformation
	const auto aumi = WinToast::configureAUMI(L"StanfordPWTLab", L"windows_logger", L"windows_logger", L"20200130");
	WinToast::instance()->setAppUserModelId(aumi);
	WinToast::instance()->initialize();

	templ.setTextField(L"Stanford PWT Lab", WinToastTemplate::FirstLine);
	templ.setTextField(L"If you have the time to answer a survey, click HERE", WinToastTemplate::SecondLine);

	TCHAR buffer[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, buffer);
	std::wstring link(buffer);
	std::wstring imageLink = link + L"\\stanford_logo.png";
	templ.setImagePath(imageLink);

	WinToast::instance()->showToast(templ, handler);

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
	return 0;
}