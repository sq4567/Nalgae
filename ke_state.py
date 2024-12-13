import ctypes
from ctypes import wintypes

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

def print_ime_stat(han10: bool):
    HWND = GetForegroundWindow()
    if HWND != 0:
        himm = ImmGetDefaultIMEWnd(HWND)

        if not han10:
            MesValue = 1
        else:
            MesValue = 5

        Stat = SendMessage(himm, WM_IME_CONTROL, MesValue, 0)
        
        # Stat 변수 콘솔 출력
        print("IME 상태 조회 결과(Stat):", Stat)
    else:
        print("포커스된 윈도우가 없습니다.")

# 예시 호출
print_ime_stat(han10=False)
