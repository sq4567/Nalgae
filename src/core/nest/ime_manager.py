"""IME 상태를 관리하는 모듈입니다."""

import logging
import win32api
import win32con
import win32gui
import time
from enum import Enum, auto
from typing import Optional, Callable, Set, Tuple

# 로거 설정
logger = logging.getLogger(__name__)

# IME 관련 상수
MAX_SYNC_RETRIES = 3
SYNC_RETRY_DELAY = 0.1
SYNC_CHECK_INTERVAL = 0.5  # seconds

class IMEState(Enum):
    """IME의 상태를 나타내는 열거형 클래스입니다."""
    ENGLISH = auto()  # 영문 입력 모드
    KOREAN = auto()   # 한글 입력 모드

class IMESyncError(Exception):
    """IME 동기화 실패 시 발생하는 예외입니다."""
    pass

class IMEManager:
    """IME 상태를 관리하는 클래스입니다."""
    
    def __init__(self):
        """IMEManager 클래스를 초기화합니다."""
        self._state = IMEState.ENGLISH
        self._state_change_callbacks: Set[Callable[[IMEState], None]] = set()
        self._last_window_handle = None
        self._last_sync_time = 0
        self._sync_failures = 0
        self._initialize_ime()
        
    def _initialize_ime(self) -> None:
        """IME 초기 상태를 설정합니다."""
        for _ in range(MAX_SYNC_RETRIES):
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
                self._sync_failures = 0
                logger.debug(f"IME initialized to {self._state}")
                return
            except Exception as e:
                logger.warning(f"IME initialization attempt failed: {e}")
                time.sleep(SYNC_RETRY_DELAY)
                
        logger.error("Failed to initialize IME after multiple attempts")
        self._state = IMEState.ENGLISH
        self._sync_failures += 1
            
    def _get_system_ime_state(self) -> Tuple[bool, Optional[IMEState]]:
        """시스템의 현재 IME 상태를 확인합니다.
        
        Returns:
            Tuple[bool, Optional[IMEState]]: (성공 여부, IME 상태)
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            ime_handle = win32api.ImmGetContext(hwnd)
            if ime_handle:
                is_korean = win32api.ImmGetConversionStatus(ime_handle)[0] != 0
                win32api.ImmReleaseContext(hwnd, ime_handle)
                return True, IMEState.KOREAN if is_korean else IMEState.ENGLISH
        except Exception as e:
            logger.error(f"Failed to get system IME state: {e}")
        return False, None
            
    def _sync_with_system(self) -> None:
        """시스템의 IME 상태와 동기화합니다."""
        current_time = time.time()
        
        # 너무 빈번한 동기화 방지
        if current_time - self._last_sync_time < SYNC_CHECK_INTERVAL:
            return
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            
            # 윈도우가 변경된 경우에만 상태 확인
            if hwnd != self._last_window_handle:
                success = False
                for _ in range(MAX_SYNC_RETRIES):
                    success, system_state = self._get_system_ime_state()
                    if success:
                        if system_state != self._state:
                            self._state = system_state
                            self._notify_state_change()
                        self._sync_failures = 0
                        break
                    time.sleep(SYNC_RETRY_DELAY)
                    
                if not success:
                    self._sync_failures += 1
                    if self._sync_failures >= MAX_SYNC_RETRIES:
                        logger.error("Critical: IME sync repeatedly failed")
                        self._handle_sync_failure()
                        
                self._last_window_handle = hwnd
                
            self._last_sync_time = current_time
        except Exception as e:
            logger.error(f"Failed to sync IME state: {e}")
            self._sync_failures += 1
            if self._sync_failures >= MAX_SYNC_RETRIES:
                self._handle_sync_failure()
            
    def _handle_sync_failure(self) -> None:
        """IME 동기화 실패 시 복구를 시도합니다."""
        logger.warning("Attempting IME recovery...")
        try:
            # IME를 강제로 영문으로 전환
            self.force_state(IMEState.ENGLISH)
            # 시스템 상태 재확인
            success, system_state = self._get_system_ime_state()
            if success:
                self._state = system_state
                self._sync_failures = 0
                logger.info("IME recovery successful")
            else:
                raise IMESyncError("Failed to recover IME state")
        except Exception as e:
            logger.error(f"IME recovery failed: {e}")
            # 마지막 수단으로 한/영 키를 물리적으로 두 번 눌러 초기화
            self._reset_ime_physical()
            
    def _reset_ime_physical(self) -> None:
        """한/영 키를 물리적으로 두 번 눌러 IME를 초기화합니다."""
        try:
            for _ in range(2):
                win32api.keybd_event(win32con.VK_HANGUL, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_HANGUL, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
            logger.info("Physical IME reset completed")
        except Exception as e:
            logger.error(f"Physical IME reset failed: {e}")

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