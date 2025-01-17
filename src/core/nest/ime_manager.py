"""IME 상태를 관리하는 모듈입니다."""

from enum import Enum, auto
import win32api
import win32con

class IMEState(Enum):
    """IME의 상태를 나타내는 열거형 클래스입니다."""
    ENGLISH = auto()     # 영어 입력 상태
    KOREAN = auto()      # 한글 입력 상태

class IMEManager:
    """IME의 상태를 관리하는 클래스입니다."""
    
    def __init__(self):
        """IMEManager 클래스를 초기화합니다."""
        self._state = self._get_current_ime_state()
        
    def _get_current_ime_state(self) -> IMEState:
        """현재 시스템의 IME 상태를 확인합니다.
        
        Returns:
            IMEState: 현재 IME 상태
        """
        # 0: 영어, 1: 한글
        ime_state = win32api.GetKeyState(win32con.VK_HANGUL) & 0x0001
        return IMEState.KOREAN if ime_state else IMEState.ENGLISH
        
    @property
    def state(self) -> IMEState:
        """현재 IME 상태를 반환합니다."""
        self._state = self._get_current_ime_state()
        return self._state
        
    def is_korean(self) -> bool:
        """현재 한글 입력 상태인지 확인합니다."""
        return self.state == IMEState.KOREAN
        
    def toggle_ime(self) -> None:
        """IME 상태를 토글합니다."""
        win32api.keybd_event(win32con.VK_HANGUL, 0, 0, 0)
        win32api.keybd_event(win32con.VK_HANGUL, 0, win32con.KEYEVENTF_KEYUP, 0)