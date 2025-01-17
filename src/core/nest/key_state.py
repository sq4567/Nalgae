"""키 상태를 관리하는 모듈입니다."""

from enum import Enum, auto

class KeyState(Enum):
    """키의 상태를 나타내는 열거형 클래스입니다."""
    NORMAL = auto()      # 일반 상태
    HOVER = auto()       # 마우스 호버 상태
    PRESSED = auto()     # 좌클릭 눌림 상태
    LOCKED = auto()      # 고정 상태
    DISABLED = auto()    # 비활성 상태

class KeyStateManager:
    """키의 상태를 관리하는 클래스입니다."""
    
    def __init__(self):
        """KeyStateManager 클래스를 초기화합니다."""
        self._state = KeyState.NORMAL
        self._is_function_key = False
        self._press_start_time = None
        
    @property
    def state(self) -> KeyState:
        """현재 키의 상태를 반환합니다."""
        return self._state
        
    def set_state(self, new_state: KeyState) -> None:
        """키의 상태를 변경합니다.
        
        Args:
            new_state (KeyState): 변경할 새로운 상태
        """
        self._state = new_state
        
    def is_active(self) -> bool:
        """키가 활성 상태인지 확인합니다."""
        return self._state != KeyState.DISABLED
        
    def is_locked(self) -> bool:
        """키가 고정 상태인지 확인합니다."""
        return self._state == KeyState.LOCKED 