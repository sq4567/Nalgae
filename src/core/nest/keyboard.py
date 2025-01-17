"""키보드의 핵심 기능을 구현하는 모듈입니다."""

from typing import Dict, Optional
import time
import win32api
import win32con

from .key_state import KeyState, KeyStateManager
from .ime_manager import IMEState, IMEManager
from .key_label import KeyLabel, KeyLabelManager

class Key:
    """하나의 키를 나타내는 클래스입니다."""
    
    def __init__(self, key_id: str, virtual_key: int, is_function_key: bool = False, long_press_threshold: float = 1.0):
        """Key 클래스를 초기화합니다.
        
        Args:
            key_id (str): 키의 고유 식별자
            virtual_key (int): Windows Virtual Key Code
            is_function_key (bool, optional): 기능 키 여부. Defaults to False.
            long_press_threshold (float, optional): 길게 누르기로 판단할 시간(초). Defaults to 1.0.
        """
        self.key_id = key_id
        self.virtual_key = virtual_key
        self.is_function_key = is_function_key
        self.long_press_threshold = long_press_threshold
        self.state_manager = KeyStateManager()
        self._press_start_time: Optional[float] = None
        
    def press(self) -> None:
        """키를 누릅니다."""
        if not self.state_manager.is_active():
            return
            
        self._press_start_time = time.time()
        self.state_manager.set_state(KeyState.PRESSED)
        
        # 실제 키 입력 시뮬레이션
        win32api.keybd_event(self.virtual_key, 0, 0, 0)
        
    def release(self) -> None:
        """키를 뗍니다."""
        if not self.state_manager.is_active():
            return
            
        # 길게 누르기 판정
        if (self.is_function_key and self._press_start_time and 
            time.time() - self._press_start_time >= self.long_press_threshold):
            self.state_manager.set_state(KeyState.LOCKED)
        else:
            self.state_manager.set_state(KeyState.NORMAL)
            
        # 실제 키 해제 시뮬레이션
        win32api.keybd_event(self.virtual_key, 0, win32con.KEYEVENTF_KEYUP, 0)
        self._press_start_time = None

class NestKeyboard:
    """화상 키보드의 핵심 기능을 구현하는 클래스입니다."""
    
    def __init__(self):
        """NestKeyboard 클래스를 초기화합니다."""
        self.keys: Dict[str, Key] = {}
        self.ime_manager = IMEManager()
        self.label_manager = KeyLabelManager()
        self._initialize_keys()
        
    def _initialize_keys(self) -> None:
        """키보드의 모든 키를 초기화합니다."""
        # 기능 키 초기화
        function_keys = {
            'shift': win32con.VK_SHIFT,
            'ctrl': win32con.VK_CONTROL,
            'alt': win32con.VK_MENU,
            'win': win32con.VK_LWIN,
            'hangul': win32con.VK_HANGUL,
            'caps_lock': win32con.VK_CAPITAL
        }
        for key_id, vk in function_keys.items():
            self.keys[key_id] = Key(key_id, vk, is_function_key=True)
            
        # 알파벳 키 초기화
        for c in range(ord('a'), ord('z') + 1):
            char = chr(c)
            self.keys[char] = Key(char, ord(char.upper()), is_function_key=False)
            
        # 숫자 키 초기화
        for num in range(10):
            num_str = str(num)
            self.keys[num_str] = Key(num_str, ord(num_str), is_function_key=False)
            
        # 특수문자 키 초기화
        special_keys = {
            '`': win32con.VK_OEM_3,
            '-': win32con.VK_OEM_MINUS,
            '=': win32con.VK_OEM_PLUS,
            '[': win32con.VK_OEM_4,
            ']': win32con.VK_OEM_6,
            '\\': win32con.VK_OEM_5,
            ';': win32con.VK_OEM_1,
            "'": win32con.VK_OEM_7,
            ',': win32con.VK_OEM_COMMA,
            '.': win32con.VK_OEM_PERIOD,
            '/': win32con.VK_OEM_2
        }
        for key_id, vk in special_keys.items():
            self.keys[key_id] = Key(key_id, vk, is_function_key=False)
            
    def press_key(self, key_id: str) -> None:
        """특정 키를 누릅니다.
        
        Args:
            key_id (str): 누를 키의 식별자
        """
        if key_id not in self.keys:
            return
            
        key = self.keys[key_id]
        
        # 한/영 키 처리
        if key_id == 'hangul':
            self.ime_manager.toggle_ime()
            return
            
        # Caps Lock 키 처리
        if key_id == 'caps_lock':
            self.label_manager.toggle_caps_lock()
            
        key.press()
        
    def release_key(self, key_id: str) -> None:
        """특정 키를 뗍니다.
        
        Args:
            key_id (str): 뗄 키의 식별자
        """
        if key_id in self.keys:
            self.keys[key_id].release()
            
    def get_key_label(self, key_id: str) -> str:
        """특정 키의 현재 레이블을 가져옵니다.
        
        Args:
            key_id (str): 레이블을 가져올 키의 식별자
            
        Returns:
            str: 현재 상태에 맞는 키 레이블
        """
        # Shift 키가 활성화되었는지 확인
        shift_active = (self.keys['shift'].state_manager.state in 
                       {KeyState.PRESSED, KeyState.LOCKED})
        
        # Alt 키가 활성화되었는지 확인
        alt_active = (self.keys['alt'].state_manager.state in 
                     {KeyState.PRESSED, KeyState.LOCKED})
        
        return self.label_manager.get_label(key_id, shift_active, alt_active)
        
    def is_key_active(self, key_id: str) -> bool:
        """특정 키가 활성 상태인지 확인합니다.
        
        Args:
            key_id (str): 확인할 키의 식별자
            
        Returns:
            bool: 키가 활성 상태이면 True
        """
        return key_id in self.keys and self.keys[key_id].state_manager.is_active() 