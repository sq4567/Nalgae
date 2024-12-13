import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)
imm32 = ctypes.WinDLL('imm32', use_last_error=True)

GetFocus = user32.GetFocus
GetFocus.restype = wintypes.HWND

ImmGetContext = imm32.ImmGetContext
ImmGetContext.argtypes = [wintypes.HWND]
ImmGetContext.restype = wintypes.HANDLE

ImmReleaseContext = imm32.ImmReleaseContext
ImmReleaseContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
ImmReleaseContext.restype = wintypes.BOOL

ImmGetConversionStatus = imm32.ImmGetConversionStatus
ImmGetConversionStatus.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD)]
ImmGetConversionStatus.restype = wintypes.BOOL

def print_ime_stat():
    hwnd = GetFocus()
    if hwnd:
        himc = ImmGetContext(hwnd)
        if himc:
            fdwConversion = wintypes.DWORD()
            fdwSentence = wintypes.DWORD()
            if ImmGetConversionStatus(himc, ctypes.byref(fdwConversion), ctypes.byref(fdwSentence)):
                # IME 상태 값 (fdwConversion)을 정수 그대로 출력
                print(fdwConversion.value)
            else:
                # 조회 실패 시 0 등의 기본값으로 처리할 수도 있음. 여기서는 실패 메시지 출력
                print("0")  
            ImmReleaseContext(hwnd, himc)
        else:
            # IME 컨텍스트를 얻지 못한 경우 0 출력
            print("0")
    else:
        # 포커스 윈도우가 없는 경우 0 출력
        print("0")

# 함수 실행 예
time.sleep(3.0)
print_ime_stat()