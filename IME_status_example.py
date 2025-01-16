import ctypes
from ctypes import wintypes
import atexit
import sys

# 윈도우즈 API 함수 및 상수 정의
try:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
except AttributeError:
    print("Windows 시스템에서만 실행 가능합니다.")
    sys.exit(1)

def set_hook():
    try:
        # 후크 프로시저 정의
        CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        
        def hook_procedure(nCode, wParam, lParam):
            if nCode >= 0:
                # 여기에 키보드 이벤트 처리 로직 추가
                pass
            return user32.CallNextHookEx(None, nCode, wParam, lParam)
        
        hook_function = CMPFUNC(hook_procedure)
        
        # 후크 설정 (NULL 모듈 핸들 사용)
        hook = user32.SetWindowsHookExA(
            13,  # WH_KEYBOARD_LL
            hook_function,
            None,  # 모듈 핸들을 NULL로 설정
            0
        )
        
        if not hook:
            error_code = ctypes.get_last_error()
            raise ctypes.WinError(error_code)
        
        return hook, hook_function
    
    except Exception as e:
        print(f"후크 설정 중 오류 발생: {e}")
        return None, None

def remove_hook(hook):
    if hook:
        try:
            user32.UnhookWindowsHookEx(hook)
        except Exception as e:
            print(f"후크 제거 중 오류 발생: {e}")

def main():
    hook, hook_function = set_hook()
    if hook:
        try:
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            remove_hook(hook)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
