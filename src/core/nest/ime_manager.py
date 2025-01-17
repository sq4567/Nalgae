"""IME 상태를 관리하는 모듈입니다."""

from enum import Enum, auto
import ctypes
from ctypes import wintypes
import win32api
import win32con
import atexit

class IMEState(Enum):
    """IME의 상태를 나타내는 열거형 클래스입니다."""
    ENGLISH = auto()     # 영어 입력 상태
    KOREAN = auto()      # 한글 입력 상태

class IMEManager:
    """IME의 상태를 관리하는 클래스입니다."""
    
    def __init__(self):
        """IMEManager 클래스를 초기화합니다."""
        self._state = self._get_current_ime_state()
        self._hook = None
        self._hook_function = None
        self._setup_hook()
        atexit.register(self._cleanup)
        
    def _get_current_ime_state(self) -> IMEState:
        """현재 시스템의 IME 상태를 확인합니다.
        
        Returns:
            IMEState: 현재 IME 상태
        """
        # 0: 영어, 1: 한글
        ime_state = win32api.GetKeyState(win32con.VK_HANGUL) & 0x0001
        return IMEState.KOREAN if ime_state else IMEState.ENGLISH
        
    def _setup_hook(self) -> None:
        """키보드 후킹을 설정합니다."""
        try:
            # 후크 프로시저 정의
            CMPFUNC = ctypes.WINFUNCTYPE(
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_void_p)
            )
            
            def hook_procedure(nCode, wParam, lParam):
                if nCode >= 0:
                    # IME 상태가 변경되었을 때 상태 업데이트
                    self._state = self._get_current_ime_state()
                return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
            
            self._hook_function = CMPFUNC(hook_procedure)
            
            # 후크 설정
            self._hook = ctypes.windll.user32.SetWindowsHookExA(
                13,  # WH_KEYBOARD_LL
                self._hook_function,
                None,
                0
            )
            
            if not self._hook:
                error_code = ctypes.get_last_error()
                raise ctypes.WinError(error_code)
                
        except Exception as e:
            print(f"후크 설정 중 오류 발생: {e}")
            self._hook = None
            self._hook_function = None
            
    def _cleanup(self) -> None:
        """후킹을 정리합니다."""
        if self._hook:
            try:
                ctypes.windll.user32.UnhookWindowsHookEx(self._hook)
            except Exception as e:
                print(f"후크 제거 중 오류 발생: {e}")
        
    @property
    def state(self) -> IMEState:
        """현재 IME 상태를 반환합니다."""
        return self._state
        
    def is_korean(self) -> bool:
        """현재 한글 입력 상태인지 확인합니다."""
        return self.state == IMEState.KOREAN
        
    def toggle_ime(self) -> None:
        """IME 상태를 토글합니다."""
        win32api.keybd_event(win32con.VK_HANGUL, 0, 0, 0)
        win32api.keybd_event(win32con.VK_HANGUL, 0, win32con.KEYEVENTF_KEYUP, 0)
        
    def __del__(self):
        """소멸자에서 후킹을 정리합니다."""
        self._cleanup()