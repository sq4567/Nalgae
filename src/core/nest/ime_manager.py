"""IME 상태를 관리하는 모듈입니다."""

import logging
import win32api
import win32con
import win32gui

from enum import Enum, auto
from typing import Optional, Callable, Set

# 로거 설정
logger = logging.getLogger(__name__)

class IMEState(Enum):
    """IME의 상태를 나타내는 열거형 클래스입니다."""
    ENGLISH = auto()  # 영문 입력 모드
    KOREAN = auto()   # 한글 입력 모드

class IMEManager:
    """IME 상태를 관리하는 클래스입니다."""
    
    def __init__(self):
        """IMEManager 클래스를 초기화합니다."""
        self._state = IMEState.ENGLISH
        self._state_change_callbacks: Set[Callable[[IMEState], None]] = set()
        self._last_window_handle = None
        self._initialize_ime()
        
    def _initialize_ime(self) -> None:
        """IME 초기 상태를 설정합니다."""
        try:
            # 현재 활성 윈도우의 IME 상태 확인
            hwnd = win32gui.GetForegroundWindow()
            ime_handle = win32api.ImmGetContext(hwnd)
            if ime_handle:
                # IME 상태 확인 (0: 영문, 1: 한글)
                is_korean = win32api.ImmGetConversionStatus(ime_handle)[0] != 0
                self._state = IMEState.KOREAN if is_korean else IMEState.ENGLISH
                win32api.ImmReleaseContext(hwnd, ime_handle)
                
            self._last_window_handle = hwnd
            logger.debug(f"IME initialized to {self._state}")
        except Exception as e:
            logger.error(f"Failed to initialize IME: {e}")
            self._state = IMEState.ENGLISH
            
    def _sync_with_system(self) -> None:
        """시스템의 IME 상태와 동기화합니다."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            
            # 윈도우가 변경된 경우에만 상태 확인
            if hwnd != self._last_window_handle:
                ime_handle = win32api.ImmGetContext(hwnd)
                if ime_handle:
                    is_korean = win32api.ImmGetConversionStatus(ime_handle)[0] != 0
                    new_state = IMEState.KOREAN if is_korean else IMEState.ENGLISH
                    
                    if new_state != self._state:
                        self._state = new_state
                        self._notify_state_change()
                        
                    win32api.ImmReleaseContext(hwnd, ime_handle)
                    
                self._last_window_handle = hwnd
        except Exception as e:
            logger.error(f"Failed to sync IME state: {e}")
            
    def toggle_ime(self) -> None:
        """IME 상태를 전환합니다."""
        try:
            # 현재 활성 윈도우의 IME 상태 전환
            hwnd = win32gui.GetForegroundWindow()
            win32api.keybd_event(win32con.VK_HANGUL, 0, 0, 0)
            win32api.keybd_event(win32con.VK_HANGUL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 상태 업데이트
            self._state = (IMEState.ENGLISH if self._state == IMEState.KOREAN 
                          else IMEState.KOREAN)
            
            self._notify_state_change()
            logger.debug(f"IME toggled to {self._state}")
        except Exception as e:
            logger.error(f"Failed to toggle IME: {e}")
            
    def force_state(self, state: IMEState) -> None:
        """IME 상태를 강제로 설정합니다.
        
        Args:
            state (IMEState): 설정할 IME 상태
        """
        if state == self._state:
            return
            
        self.toggle_ime()
        
    def add_state_change_callback(self, callback: Callable[[IMEState], None]) -> None:
        """IME 상태 변경 시 호출될 콜백을 등록합니다.
        
        Args:
            callback (Callable[[IMEState], None]): 호출될 콜백 함수
        """
        self._state_change_callbacks.add(callback)
        
    def remove_state_change_callback(self, callback: Callable[[IMEState], None]) -> None:
        """등록된 IME 상태 변경 콜백을 제거합니다.
        
        Args:
            callback (Callable[[IMEState], None]): 제거할 콜백 함수
        """
        self._state_change_callbacks.discard(callback)
        
    def _notify_state_change(self) -> None:
        """IME 상태 변경을 구독자들에게 알립니다."""
        for callback in self._state_change_callbacks:
            try:
                callback(self._state)
            except Exception as e:
                logger.error(f"Error in IME state change callback: {e}")
                
    def is_korean(self) -> bool:
        """현재 한글 입력 모드인지 확인합니다.
        
        Returns:
            bool: 한글 입력 모드이면 True
        """
        self._sync_with_system()  # 시스템 상태와 동기화
        return self._state == IMEState.KOREAN