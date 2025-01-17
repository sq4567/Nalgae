"""키 레이블을 관리하는 모듈입니다."""

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class KeyLabel:
    """키의 레이블 정보를 담는 데이터 클래스입니다."""
    normal: str              # 기본 레이블
    shift: Optional[str]     # Shift 키와 함께 눌렀을 때의 레이블
    alt: Optional[str]       # Alt 키와 함께 눌렀을 때의 레이블

class KeyLabelManager:
    """키의 레이블을 관리하는 클래스입니다."""
    
    def __init__(self):
        """KeyLabelManager 클래스를 초기화합니다."""
        self._labels: Dict[str, KeyLabel] = {}
        self._is_caps_lock = False
        self._initialize_labels()
        
    def _initialize_labels(self) -> None:
        """기본 키 레이블을 초기화합니다."""
        # 영문 알파벳
        for c in range(ord('a'), ord('z') + 1):
            char = chr(c)
            self._labels[char] = KeyLabel(
                normal=char,
                shift=char.upper(),
                alt=None
            )
            
        # 숫자 키
        number_shifts = {
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')'
        }
        for num, shift in number_shifts.items():
            self._labels[num] = KeyLabel(
                normal=num,
                shift=shift,
                alt=None
            )
            
        # 특수문자 키
        special_chars = {
            '`': ('`', '~'), '-': ('-', '_'), '=': ('=', '+'),
            '[': ('[', '{'), ']': (']', '}'), '\\': ('\\', '|'),
            ';': (';', ':'), "'": ("'", '"'), ',': (',', '<'),
            '.': ('.', '>'), '/': ('/', '?')
        }
        for key, (normal, shift) in special_chars.items():
            self._labels[key] = KeyLabel(
                normal=normal,
                shift=shift,
                alt=None
            )
            
    def get_label(self, key: str, shift: bool = False, alt: bool = False) -> str:
        """키의 현재 레이블을 반환합니다.
        
        Args:
            key (str): 키 식별자
            shift (bool): Shift 키가 눌렸는지 여부
            alt (bool): Alt 키가 눌렸는지 여부
            
        Returns:
            str: 현재 상태에 맞는 키 레이블
        """
        if key not in self._labels:
            return key
            
        label = self._labels[key]
        if alt and label.alt:
            return label.alt
        if shift and label.shift:
            return label.shift
        
        # Caps Lock이 켜져있고 알파벳인 경우
        if self._is_caps_lock and key.isalpha():
            return label.normal.upper() if not shift else label.normal.lower()
            
        return label.normal
        
    def toggle_caps_lock(self) -> None:
        """Caps Lock 상태를 토글합니다."""
        self._is_caps_lock = not self._is_caps_lock
        
    @property
    def is_caps_lock(self) -> bool:
        """현재 Caps Lock 상태를 반환합니다."""
        return self._is_caps_lock 