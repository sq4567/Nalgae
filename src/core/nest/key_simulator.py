"""키 입력 시뮬레이션을 담당하는 모듈입니다."""

import win32api
import win32con
from typing import Dict, Set

class KeySimulator:
    """키 입력을 시뮬레이션하는 클래스입니다."""
    
    # 키 코드와 Windows Virtual Key Code 매핑
    VK_MAP = {
        # 알파벳
        **{chr(c): ord(c.upper()) for c in range(ord('a'), ord('z') + 1)},
        # 숫자
        **{str(n): ord(str(n)) for n in range(10)},
        # 기능 키
        'shift': win32con.VK_SHIFT,
        'ctrl': win32con.VK_CONTROL,
        'alt': win32con.VK_MENU,
        'win': win32con.VK_LWIN,
        'hangul': win32con.VK_HANGUL,
        'caps_lock': win32con.VK_CAPITAL,
        # 특수문자
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
    
    def __init__(self):
        """KeySimulator 클래스를 초기화합니다."""
        self._active_keys: Set[str] = set()  # 현재 눌린 키들
        
    def press_key(self, key_code: str) -> None:
        """키를 누릅니다.
        
        Args:
            key_code (str): 누를 키의 코드
        """
        if key_code not in self.VK_MAP:
            return
            
        vk = self.VK_MAP[key_code]
        win32api.keybd_event(vk, 0, 0, 0)
        self._active_keys.add(key_code)
        
    def release_key(self, key_code: str) -> None:
        """키를 뗍니다.
        
        Args:
            key_code (str): 뗄 키의 코드
        """
        if key_code not in self.VK_MAP:
            return
            
        vk = self.VK_MAP[key_code]
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        self._active_keys.discard(key_code)
        
    def press_keys(self, key_codes: Set[str]) -> None:
        """여러 키를 동시에 누릅니다.
        
        Args:
            key_codes (Set[str]): 누를 키들의 코드
        """
        for key_code in key_codes:
            self.press_key(key_code)
            
    def release_keys(self, key_codes: Set[str]) -> None:
        """여러 키를 동시에 뗍니다.
        
        Args:
            key_codes (Set[str]): 뗄 키들의 코드
        """
        for key_code in key_codes:
            self.release_key(key_code)
            
    def release_all_keys(self) -> None:
        """현재 눌린 모든 키를 뗍니다."""
        keys_to_release = self._active_keys.copy()
        for key_code in keys_to_release:
            self.release_key(key_code)
            
    @property
    def active_keys(self) -> Set[str]:
        """현재 눌린 키들의 집합을 반환합니다."""
        return self._active_keys.copy() 