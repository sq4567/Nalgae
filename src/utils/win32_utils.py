import ctypes
from ctypes import wintypes
import win32api
import win32con

# 윈도우즈 API 함수 및 상수 정의
user32 = ctypes.WinDLL('user32', use_last_error=True)
imm32 = ctypes.WinDLL('imm32', use_last_error=True)

GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = wintypes.HWND
GetForegroundWindow.argtypes = []

SendMessage = user32.SendMessageW
SendMessage.restype = wintypes.LPARAM
SendMessage.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

ImmGetDefaultIMEWnd = imm32.ImmGetDefaultIMEWnd
ImmGetDefaultIMEWnd.restype = wintypes.HWND
ImmGetDefaultIMEWnd.argtypes = [wintypes.HWND]

WM_IME_CONTROL = 0x283

def is_hangul_mode() -> bool:
    """현재 한글 입력 모드인지 확인합니다."""
    hwnd = GetForegroundWindow()
    if hwnd:
        himm = ImmGetDefaultIMEWnd(hwnd)
        stat = SendMessage(himm, WM_IME_CONTROL, 1, 0)
        print(f"IME 상태: {stat}")  # 상태값 출력
        return stat == 1
    return False

def switch_keyboard_layout():
    """한/영 전환을 수행합니다."""
    # 한/영 키 시뮬레이션
    win32api.keybd_event(win32con.VK_HANGUL, 0, 0, 0)  # 한/영 키 누름
    win32api.keybd_event(win32con.VK_HANGUL, 0, win32con.KEYEVENTF_KEYUP, 0)  # 한/영 키 뗌