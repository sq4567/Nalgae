"""키보드의 시각/청각 피드백을 관리하는 모듈입니다."""

import logging
from typing import Dict
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl

logger = logging.getLogger(__name__)

class FeedbackManager:
    """키보드의 피드백을 관리하는 클래스입니다."""
    
    def __init__(self):
        """FeedbackManager 클래스를 초기화합니다."""
        self._visual_enabled = True
        self._sound_enabled = True
        self._key_colors: Dict[str, QColor] = {}
        self._key_sounds: Dict[str, QSoundEffect] = {}
        
    def initialize_key(self, key_id: str, color: QColor) -> None:
        """키의 초기 상태를 설정합니다."""
        self._key_colors[key_id] = color
        
    def play_key_press_sound(self, key_id: str) -> None:
        """키 누름 소리를 재생합니다."""
        if not self._sound_enabled:
            return
            
        if key_id in self._key_sounds:
            self._key_sounds[key_id].play()
            
    def play_key_release_sound(self, key_id: str) -> None:
        """키 뗌 소리를 재생합니다."""
        if not self._sound_enabled:
            return
            
        if key_id in self._key_sounds:
            self._key_sounds[key_id].play()
            
    @property
    def visual_enabled(self) -> bool:
        """시각적 피드백 활성화 여부를 반환합니다."""
        return self._visual_enabled
        
    @visual_enabled.setter
    def visual_enabled(self, value: bool) -> None:
        """시각적 피드백 활성화 여부를 설정합니다."""
        self._visual_enabled = value
        
    @property
    def sound_enabled(self) -> bool:
        """소리 피드백 활성화 여부를 반환합니다."""
        return self._sound_enabled
        
    @sound_enabled.setter
    def sound_enabled(self, value: bool) -> None:
        """소리 피드백 활성화 여부를 설정합니다."""
        self._sound_enabled = value 