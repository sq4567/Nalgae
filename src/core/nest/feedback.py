"""키보드 피드백을 관리하는 모듈입니다."""

import logging
from enum import Enum
from typing import Dict, Optional
from pathlib import Path
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QObject, QUrl
from PySide6.QtGui import QColor

# 로거 설정
logger = logging.getLogger(__name__)

class KeySwitchType(Enum):
    """키보드 스위치의 종류를 나타내는 열거형 클래스입니다."""
    ALPACA = "alpaca"          # Alpaca
    BLACK_INK = "blackink"     # Black Ink
    BLUE_ALPS = "bluealps"     # Blue Alps
    BOX_NAVY = "boxnavy"       # Box Navy
    BUCKLING = "buckling"      # Buckling
    CREAM = "cream"            # Cream
    HOLY_PANDA = "holypanda"   # Holy Panda
    MX_BLACK = "mxblack"       # Cherry MX Black
    MX_BLUE = "mxblue"         # Cherry MX Blue
    MX_BROWN = "mxbrown"       # Cherry MX Brown
    RED_INK = "redink"         # Red Ink
    TOPRE = "topre"            # Topre
    TURQUOISE = "turquoise"    # Turquoise

class VisualFeedback(QObject):
    """키의 시각적 피드백을 관리하는 클래스입니다."""
    
    def __init__(self, initial_color: QColor):
        """VisualFeedback 클래스를 초기화합니다.
        
        Args:
            initial_color (QColor): 초기 색상
        """
        super().__init__()
        self._color = initial_color
        self._animation = QPropertyAnimation(self, b"color")
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.setDuration(100)  # 100ms
        
    def get_color(self) -> QColor:
        """현재 색상을 반환합니다."""
        return self._color
        
    def set_color(self, color: QColor) -> None:
        """색상을 설정합니다."""
        self._color = color
        
    color = Property(QColor, get_color, set_color)
    
    def animate_to(self, target_color: QColor, duration: int = 100) -> None:
        """특정 색상으로 애니메이션을 수행합니다.
        
        Args:
            target_color (QColor): 목표 색상
            duration (int, optional): 애니메이션 지속 시간(ms). 기본값은 100
        """
        self._animation.setStartValue(self._color)
        self._animation.setEndValue(target_color)
        self._animation.setDuration(duration)
        self._animation.start()

class FeedbackManager:
    """키보드의 피드백을 관리하는 클래스입니다."""
    
    # 특수 키 사운드 매핑
    SPECIAL_KEYS = {'backspace', 'enter', 'space'}
    
    def __init__(self):
        """FeedbackManager 클래스를 초기화합니다."""
        super().__init__()
        self._visual_enabled = True
        self._sound_enabled = True
        self._visual_feedbacks: Dict[str, VisualFeedback] = {}
        self._sound_cache: Dict[str, QSoundEffect] = {}
        self._current_switch = KeySwitchType.MX_BROWN
        
        # 사운드 파일 경로 설정
        self._sound_dir = Path(__file__).parent.parent.parent.parent / "assets" / "sounds" / "keyboard"
        
    def _get_sound_file(self, key_id: str, is_press: bool) -> Optional[Path]:
        """키에 해당하는 사운드 파일 경로를 반환합니다.
        
        Args:
            key_id (str): 키 식별자
            is_press (bool): 키를 누르는 소리인지 여부
            
        Returns:
            Optional[Path]: 사운드 파일 경로. 파일이 없으면 None
        """
        switch_dir = self._sound_dir / self._current_switch.value
        sound_type = "press" if is_press else "release"
        
        # 특수 키 처리
        key_lower = key_id.lower()
        if key_lower in self.SPECIAL_KEYS:
            sound_file = switch_dir / sound_type / f"{key_lower.upper()}.mp3"
            return sound_file if sound_file.exists() else None
            
        # 일반 키 처리 (모든 일반 키는 GENERIC.mp3 사용)
        sound_file = switch_dir / sound_type / "GENERIC.mp3"
        return sound_file if sound_file.exists() else None
        
    def set_switch_type(self, switch_type: KeySwitchType) -> None:
        """키보드 스위치 타입을 설정합니다.
        
        Args:
            switch_type (KeySwitchType): 설정할 스위치 타입
        """
        if self._current_switch != switch_type:
            self._current_switch = switch_type
            # 캐시 초기화
            self._sound_cache.clear()
            logger.info(f"Keyboard switch type changed to {switch_type.name}")
        
    def play_key_press_sound(self, key_id: str) -> None:
        """키 누름 소리를 재생합니다.
        
        Args:
            key_id (str): 키 식별자
        """
        if not self._sound_enabled:
            return
            
        try:
            sound_file = self._get_sound_file(key_id, True)
            if sound_file:
                sound = self._load_sound(sound_file)
                if sound:
                    sound.play()
            else:
                logger.warning(f"No press sound file found for key: {key_id}")
        except Exception as e:
            logger.error(f"Failed to play key press sound: {e}")
            
    def play_key_release_sound(self, key_id: str) -> None:
        """키 뗌 소리를 재생합니다.
        
        Args:
            key_id (str): 키 식별자
        """
        if not self._sound_enabled:
            return
            
        try:
            sound_file = self._get_sound_file(key_id, False)
            if sound_file:
                sound = self._load_sound(sound_file)
                if sound:
                    sound.play()
            else:
                logger.warning(f"No release sound file found for key: {key_id}")
        except Exception as e:
            logger.error(f"Failed to play key release sound: {e}")
            
    def _load_sound(self, sound_file: Path) -> Optional[QSoundEffect]:
        """사운드 파일을 로드하거나 캐시에서 가져옵니다.
        
        Args:
            sound_file (Path): 사운드 파일 경로
            
        Returns:
            Optional[QSoundEffect]: 로드된 사운드 객체. 실패 시 None
        """
        cache_key = str(sound_file)
        if cache_key in self._sound_cache:
            return self._sound_cache[cache_key]
            
        try:
            if sound_file.exists():
                sound = QSoundEffect()
                sound.setSource(QUrl.fromLocalFile(str(sound_file)))
                sound.setLoopCount(1)  # 한 번만 재생
                sound.setVolume(1.0)   # 최대 볼륨
                
                # 로딩 완료 대기
                if sound.status() == QSoundEffect.Status.Ready:
                    self._sound_cache[cache_key] = sound
                    return sound
                else:
                    logger.warning(f"Sound file loading failed: {sound_file}")
                    return None
            else:
                logger.warning(f"Sound file not found: {sound_file}")
                return None
        except Exception as e:
            logger.error(f"Failed to load sound file: {e}")
            return None
            
    def cleanup(self) -> None:
        """리소스를 정리합니다."""
        # 사운드 캐시 정리
        self._sound_cache.clear()
        
    @property
    def current_switch_type(self) -> KeySwitchType:
        """현재 설정된 키보드 스위치 타입을 반환합니다."""
        return self._current_switch
        
    def initialize_key(self, key_id: str, initial_color: QColor) -> None:
        """새로운 키의 피드백을 초기화합니다.
        
        Args:
            key_id (str): 키 식별자
            initial_color (QColor): 초기 색상
        """
        self._visual_feedbacks[key_id] = VisualFeedback(initial_color)
        
    def animate_key(self, key_id: str, target_color: QColor, 
                   duration: int = 100) -> None:
        """키의 색상 애니메이션을 수행합니다.
        
        Args:
            key_id (str): 키 식별자
            target_color (QColor): 목표 색상
            duration (int, optional): 애니메이션 지속 시간(ms). 기본값은 100
        """
        if not self._visual_enabled or key_id not in self._visual_feedbacks:
            return
            
        self._visual_feedbacks[key_id].animate_to(target_color, duration)
        
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
        
    def get_current_color(self, key_id: str) -> Optional[QColor]:
        """키의 현재 색상을 반환합니다.
        
        Args:
            key_id (str): 키 식별자
            
        Returns:
            Optional[QColor]: 현재 색상. 키가 없으면 None
        """
        if key_id not in self._visual_feedbacks:
            return None
        return self._visual_feedbacks[key_id].get_color() 