"""키 레이블을 관리하는 모듈입니다."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

@dataclass
class KeyLabel:
    """키의 레이블 정보를 담는 데이터 클래스입니다."""
    normal: str              # 기본 레이블
    shift: Optional[str]     # Shift 키와 함께 눌렀을 때의 레이블
    korean: Optional[str]    # 한글 모드일 때의 레이블
    korean_shift: Optional[str]  # 한글 모드에서 Shift와 함께 눌렀을 때의 레이블

class KeyLabelManager:
    """키의 레이블을 관리하는 클래스입니다."""
    
    def __init__(self):
        """KeyLabelManager 클래스를 초기화합니다."""
        self._labels: Dict[str, KeyLabel] = {}
        self._is_caps_lock = False
        self._initialize_labels()
        
    def _initialize_labels(self) -> None:
        """기본 키 레이블을 초기화합니다."""
        # 한글 자음
        consonants = {
            'q': ('ㅂ', 'ㅃ'), 'w': ('ㅈ', 'ㅉ'), 'e': ('ㄷ', 'ㄸ'),
            'r': ('ㄱ', 'ㄲ'), 't': ('ㅅ', 'ㅆ'), 'a': ('ㅁ', None),
            's': ('ㄴ', None), 'd': ('ㅇ', None), 'f': ('ㄹ', None),
            'g': ('ㅎ', None), 'z': ('ㅋ', None), 'x': ('ㅌ', None),
            'c': ('ㅊ', None), 'v': ('ㅍ', None)
        }
        
        # 한글 모음
        vowels = {
            'y': ('ㅛ', None), 'u': ('ㅕ', None), 'i': ('ㅑ', None),
            'o': ('ㅐ', 'ㅒ'), 'p': ('ㅔ', 'ㅖ'), 'h': ('ㅗ', None),
            'j': ('ㅓ', None), 'k': ('ㅏ', None), 'l': ('ㅣ', None),
            'b': ('ㅠ', None), 'n': ('ㅜ', None), 'm': ('ㅡ', None)
        }
        
        # 영문 알파벳
        for c in range(ord('a'), ord('z') + 1):
            char = chr(c)
            korean_label = None
            korean_shift = None
            
            # 자음 처리
            if char in consonants:
                korean_label, korean_shift = consonants[char]
            # 모음 처리
            elif char in vowels:
                korean_label, korean_shift = vowels[char]
                
            self._labels[char] = KeyLabel(
                normal=char,
                shift=char.upper(),
                korean=korean_label,
                korean_shift=korean_shift
            )
            
        # 숫자 키
        number_shifts = {
            '1': ('!', '1', '!'), '2': ('@', '2', '@'), '3': ('#', '3', '#'),
            '4': ('$', '4', '$'), '5': ('%', '5', '%'), '6': ('^', '6', '^'),
            '7': ('&', '7', '&'), '8': ('*', '8', '*'), '9': ('(', '9', '('),
            '0': (')', '0', ')')
        }
        for num, (shift, korean, korean_shift) in number_shifts.items():
            self._labels[num] = KeyLabel(
                normal=num,
                shift=shift,
                korean=korean,
                korean_shift=korean_shift
            )
            
        # 특수문자 키
        special_chars = {
            '`': ('`', '~', '`', '~'),
            '-': ('-', '_', '-', '_'),
            '=': ('=', '+', '=', '+'),
            '[': ('[', '{', '[', '{'),
            ']': (']', '}', ']', '}'),
            '\\': ('\\', '|', '\\', '|'),
            ';': (';', ':', ';', ':'),
            "'": ("'", '"', "'", '"'),
            ',': (',', '<', ',', '<'),
            '.': ('.', '>', '.', '>'),
            '/': ('/', '?', '/', '?')
        }
        for key, (normal, shift, korean, korean_shift) in special_chars.items():
            self._labels[key] = KeyLabel(
                normal=normal,
                shift=shift,
                korean=korean,
                korean_shift=korean_shift
            )
            
    def get_label(self, key_id: str, shift: bool = False, is_korean: bool = False) -> str:
        """키의 현재 레이블을 반환합니다.
        
        Args:
            key_id (str): 키 식별자
            shift (bool): Shift 키가 눌렸는지 여부
            is_korean (bool): 한글 모드인지 여부
            
        Returns:
            str: 현재 상태에 맞는 키 레이블
        """
        if key_id not in self._labels:
            return key_id
            
        label = self._labels[key_id]
        
        # 한글 모드
        if is_korean:
            if shift and label.korean_shift:
                return label.korean_shift
            if label.korean:
                return label.korean
                
        # 영문 모드
        if shift and label.shift:
            return label.shift
        
        # Caps Lock이 켜져있고 알파벳인 경우
        if self._is_caps_lock and key_id.isalpha():
            return label.normal.upper() if not shift else label.normal.lower()
            
        return label.normal
        
    def toggle_caps_lock(self) -> None:
        """Caps Lock 상태를 토글합니다."""
        self._is_caps_lock = not self._is_caps_lock
        
    @property
    def is_caps_lock(self) -> bool:
        """현재 Caps Lock 상태를 반환합니다."""
        return self._is_caps_lock