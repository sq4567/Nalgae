"""키보드의 핵심 기능을 구현하는 모듈입니다."""

import logging
from typing import Dict, Optional, Tuple, Set
import time
import win32api
import win32con
from PySide6.QtGui import QColor

from .key_state import KeyState, KeyStateManager, InvalidStateTransitionError
from .ime_manager import IMEState, IMEManager
from .key_label import KeyLabel, KeyLabelManager
from .key_simulator import KeySimulator

# 로거 설정
logger = logging.getLogger(__name__)

class Key:
    """키보드의 개별 키를 나타내는 클래스입니다."""

    def __init__(self, key_code: str, label: KeyLabel, 
                 is_function_key: bool = False,
                 long_press_threshold: float = 1.0):
        """Key 클래스를 초기화합니다.
        
        Args:
            key_code (str): 키 코드
            label (KeyLabel): 키 레이블
            is_function_key (bool, optional): 기능 키 여부. 기본값은 False
            long_press_threshold (float, optional): 길게 누름 판정 시간(초). 기본값은 1.0
        """
        self._key_code = key_code
        self._label = label
        self._is_function_key = is_function_key
        self._long_press_threshold = long_press_threshold
        self._press_start_time = None
        
        # 상태 관리자 초기화
        self._state_manager = KeyStateManager()
        
        # 상태별 색상 정의
        self._colors = {
            KeyState.NORMAL: QColor("#FFFFFF"),    # 흰색
            KeyState.HOVER: QColor("#E0E0E0"),     # 연한 회색
            KeyState.PRESSED: QColor("#BDBDBD"),   # 진한 회색
            KeyState.LOCKED: QColor("#90CAF9"),    # 연한 파란색
            KeyState.DISABLED: QColor("#F5F5F5")   # 매우 연한 회색
        }
        
        # 상태 변경 콜백 등록
        for state in KeyState:
            self._state_manager.add_state_change_callback(
                state, self._on_state_change
            )
    
    @property
    def key_code(self) -> str:
        """키 코드를 반환합니다."""
        return self._key_code
    
    @property
    def label(self) -> KeyLabel:
        """키 레이블을 반환합니다."""
        return self._label
    
    @property
    def is_function_key(self) -> bool:
        """기능 키 여부를 반환합니다."""
        return self._is_function_key
    
    @property
    def state(self) -> KeyState:
        """현재 키의 상태를 반환합니다."""
        return self._state_manager.state
    
    @property
    def previous_state(self) -> Optional[KeyState]:
        """이전 키의 상태를 반환합니다."""
        return self._state_manager.previous_state
    
    @property
    def color(self) -> QColor:
        """현재 상태에 따른 키의 색상을 반환합니다."""
        return self._colors[self.state]
    
    def set_color(self, state: KeyState, color: QColor) -> None:
        """특정 상태의 키 색상을 설정합니다.
        
        Args:
            state (KeyState): 색상을 변경할 상태
            color (QColor): 새로운 색상
        """
        self._colors[state] = color
    
    def press(self) -> None:
        """키를 누릅니다."""
        if not self._state_manager.is_active():
            return
            
        try:
            self._state_manager.set_state(KeyState.PRESSED)
            self._press_start_time = time.time()
        except InvalidStateTransitionError:
            logger.warning(f"Invalid key press attempt on key {self._key_code}")
    
    def release(self) -> None:
        """키를 뗍니다."""
        if not self._state_manager.is_active():
            return
            
        try:
            # 길게 누름 여부 확인
            if (self._press_start_time and 
                time.time() - self._press_start_time >= self._long_press_threshold):
                self._state_manager.set_state(KeyState.LOCKED)
            else:
                self._state_manager.set_state(KeyState.NORMAL)
                
            self._press_start_time = None
        except InvalidStateTransitionError:
            logger.warning(f"Invalid key release attempt on key {self._key_code}")
    
    def hover(self) -> None:
        """키에 마우스를 올립니다."""
        if not self._state_manager.is_active():
            return
            
        try:
            if self.state not in {KeyState.PRESSED, KeyState.LOCKED}:
                self._state_manager.set_state(KeyState.HOVER)
        except InvalidStateTransitionError:
            logger.warning(f"Invalid hover attempt on key {self._key_code}")
    
    def unhover(self) -> None:
        """키에서 마우스를 뗍니다."""
        if not self._state_manager.is_active():
            return
            
        try:
            if self.state == KeyState.HOVER:
                self._state_manager.set_state(KeyState.NORMAL)
        except InvalidStateTransitionError:
            logger.warning(f"Invalid unhover attempt on key {self._key_code}")
    
    def toggle_lock(self) -> None:
        """키의 잠금 상태를 토글합니다."""
        if not self._state_manager.is_active():
            return
            
        try:
            if self.state == KeyState.LOCKED:
                self._state_manager.set_state(KeyState.NORMAL)
            elif self.state == KeyState.NORMAL:
                self._state_manager.set_state(KeyState.LOCKED)
        except InvalidStateTransitionError:
            logger.warning(f"Invalid lock toggle attempt on key {self._key_code}")
    
    def disable(self) -> None:
        """키를 비활성화합니다."""
        self._state_manager.disable()
    
    def enable(self) -> None:
        """키를 활성화합니다."""
        self._state_manager.enable()
    
    def is_active(self) -> bool:
        """키가 활성 상태인지 확인합니다."""
        return self._state_manager.is_active()
    
    def is_locked(self) -> bool:
        """키가 잠금 상태인지 확인합니다."""
        return self._state_manager.is_locked()
    
    def _on_state_change(self, new_state: KeyState) -> None:
        """상태 변경 시 호출되는 콜백 메서드입니다.
        
        Args:
            new_state (KeyState): 새로운 상태
        """
        logger.debug(f"Key {self._key_code} state changed to {new_state}")
        # 추가적인 상태 변경 처리 로직이 필요한 경우 여기에 구현

class NestKeyboard:
    """화상 키보드의 핵심 기능을 구현하는 클래스입니다."""
    
    def __init__(self):
        """NestKeyboard 클래스를 초기화합니다."""
        self._keys: Dict[str, Key] = {}
        self._ime_manager = IMEManager()
        self._label_manager = KeyLabelManager()
        self._key_simulator = KeySimulator()
        self._active_function_keys: Set[str] = set()
        
        # IME 상태 변경 콜백 등록
        self._ime_manager.add_state_change_callback(self._on_ime_state_change)
        
        self._initialize_keys()
        
    def _initialize_keys(self) -> None:
        """키보드의 모든 키를 초기화합니다."""
        # 기능 키 초기화
        function_keys = {
            'shift': ('Shift', True),
            'ctrl': ('Ctrl', True),
            'alt': ('Alt', True),
            'win': ('Win', True),
            'hangul': ('한/영', True),
            'caps_lock': ('Caps', True)
        }
        for key_id, (label_text, is_function) in function_keys.items():
            label = self._label_manager.create_label(key_id, label_text)
            self._keys[key_id] = Key(key_id, label, is_function_key=is_function)
            
        # 알파벳 키 초기화
        for c in range(ord('a'), ord('z') + 1):
            char = chr(c)
            label = self._label_manager.create_label(char, char.upper())
            self._keys[char] = Key(char, label)
            
        # 숫자 키 초기화
        for num in range(10):
            num_str = str(num)
            label = self._label_manager.create_label(num_str, num_str)
            self._keys[num_str] = Key(num_str, label)
            
        # 특수문자 키 초기화
        special_keys = {
            '`': ('`', '~'),
            '-': ('-', '_'),
            '=': ('=', '+'),
            '[': ('[', '{'),
            ']': (']', '}'),
            '\\': ('\\', '|'),
            ';': (';', ':'),
            "'": ("'", '"'),
            ',': (',', '<'),
            '.': ('.', '>'),
            '/': ('/', '?')
        }
        for key_id, (normal, shift) in special_keys.items():
            label = self._label_manager.create_label(key_id, normal, shift_label=shift)
            self._keys[key_id] = Key(key_id, label)
            
    def _update_function_keys(self, key_id: str, is_pressed: bool) -> None:
        """기능 키 상태를 업데이트합니다.
        
        Args:
            key_id (str): 기능 키의 식별자
            is_pressed (bool): 눌림 여부
        """
        key = self._keys[key_id]
        if not key.is_function_key:
            return
            
        if is_pressed:
            self._active_function_keys.add(key_id)
            self._key_simulator.press_key(key_id)
        else:
            if not key.is_locked():
                self._active_function_keys.discard(key_id)
                self._key_simulator.release_key(key_id)
                
    def _on_ime_state_change(self, new_state: IMEState) -> None:
        """IME 상태 변경 시 호출되는 콜백 메서드입니다.
        
        Args:
            new_state (IMEState): 새로운 IME 상태
        """
        # Caps Lock이 켜져 있고 영문 모드로 전환된 경우 Caps Lock 해제
        if (new_state == IMEState.ENGLISH and 
            self._label_manager.is_caps_lock and 
            'caps_lock' in self._keys):
            self._keys['caps_lock'].release()
            self._label_manager.toggle_caps_lock()
            
        logger.debug(f"IME state changed to {new_state}")
        
    def handle_mouse_move(self, key_id: Optional[str]) -> None:
        """마우스 이동 이벤트를 처리합니다.
        
        Args:
            key_id (Optional[str]): 마우스가 위치한 키의 식별자. 키 위에 없으면 None
        """
        # 이전에 호버 상태였던 키들의 호버 상태 해제
        for k_id, key in self._keys.items():
            if k_id != key_id:
                key.unhover()
                
        # 현재 마우스가 위치한 키의 호버 상태 설정
        if key_id in self._keys:
            self._keys[key_id].hover()
            
    def handle_mouse_press(self, key_id: str) -> None:
        """마우스 클릭 이벤트를 처리합니다.
        
        Args:
            key_id (str): 클릭된 키의 식별자
        """
        if key_id not in self._keys:
            return
            
        key = self._keys[key_id]
        
        # 한/영 키 처리
        if key_id == 'hangul':
            self._ime_manager.toggle_ime()
            return
            
        # Caps Lock 키 처리
        if key_id == 'caps_lock':
            # 한글 모드에서는 영문 모드로 전환
            if self._ime_manager.is_korean():
                self._ime_manager.force_state(IMEState.ENGLISH)
            self._label_manager.toggle_caps_lock()
            return
            
        key.press()
        
        # 기능 키 상태 업데이트
        if key.is_function_key:
            self._update_function_keys(key_id, True)
        else:
            # 일반 키는 활성화된 기능 키들과 함께 시뮬레이션
            self._key_simulator.press_key(key_id)
            
    def handle_mouse_release(self, key_id: str) -> None:
        """마우스 클릭 해제 이벤트를 처리합니다.
        
        Args:
            key_id (str): 해제된 키의 식별자
        """
        if key_id not in self._keys:
            return
            
        key = self._keys[key_id]
        key.release()
        
        # 기능 키 처리
        if key.is_function_key:
            self._update_function_keys(key_id, False)
        else:
            # 일반 키 해제
            self._key_simulator.release_key(key_id)
            
    def cleanup(self) -> None:
        """키보드 정리 작업을 수행합니다."""
        # IME 콜백 제거
        self._ime_manager.remove_state_change_callback(self._on_ime_state_change)
        
        # 모든 키 해제
        self._key_simulator.release_all_keys()
        self._active_function_keys.clear()
        
    def get_key_color(self, key_id: str) -> Optional[QColor]:
        """특정 키의 현재 색상을 가져옵니다.
        
        Args:
            key_id (str): 색상을 가져올 키의 식별자
            
        Returns:
            Optional[QColor]: 키의 현재 색상. 키가 없으면 None
        """
        if key_id not in self._keys:
            return None
        return self._keys[key_id].color
        
    def set_key_color(self, key_id: str, state: KeyState, color: QColor) -> None:
        """특정 키의 특정 상태 색상을 설정합니다.
        
        Args:
            key_id (str): 색상을 설정할 키의 식별자
            state (KeyState): 색상을 설정할 상태
            color (QColor): 새로운 색상
        """
        if key_id in self._keys:
            self._keys[key_id].set_color(state, color)
        
    def get_key_label(self, key_id: str) -> str:
        """특정 키의 현재 레이블을 가져옵니다.
        
        Args:
            key_id (str): 레이블을 가져올 키의 식별자
            
        Returns:
            str: 현재 상태에 맞는 키 레이블
        """
        if key_id not in self._keys:
            return ""
            
        key = self._keys[key_id]
        
        # Shift 키가 활성화되었는지 확인
        shift_active = any(self._keys[k].is_locked() for k in self._active_function_keys 
                         if k == 'shift')
        
        # IME 상태 확인
        is_korean = self._ime_manager.is_korean()
        
        return key.label.get_label(shift_active, is_korean)
        
    def is_key_active(self, key_id: str) -> bool:
        """특정 키가 활성 상태인지 확인합니다.
        
        Args:
            key_id (str): 확인할 키의 식별자
            
        Returns:
            bool: 키가 활성 상태이면 True
        """
        return key_id in self._keys and self._keys[key_id].is_active()