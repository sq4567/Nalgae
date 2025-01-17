"""키 상태를 관리하는 모듈입니다."""

from enum import Enum, auto
from typing import Dict, Set, Optional, Callable

class KeyState(Enum):
    """키의 상태를 나타내는 열거형 클래스입니다."""
    NORMAL = auto()      # 일반 상태
    HOVER = auto()       # 마우스 호버 상태
    PRESSED = auto()     # 좌클릭 눌림 상태
    LOCKED = auto()      # 고정 상태
    DISABLED = auto()    # 비활성 상태

class InvalidStateTransitionError(Exception):
    """유효하지 않은 상태 전이 시 발생하는 예외입니다."""
    pass

class KeyStateManager:
    """키의 상태를 관리하는 클래스입니다."""
    
    # 상태 전이 규칙 정의
    VALID_TRANSITIONS = {
        KeyState.NORMAL: {KeyState.HOVER, KeyState.PRESSED, KeyState.DISABLED},
        KeyState.HOVER: {KeyState.NORMAL, KeyState.PRESSED, KeyState.DISABLED},
        KeyState.PRESSED: {KeyState.NORMAL, KeyState.HOVER, KeyState.LOCKED, KeyState.DISABLED},
        KeyState.LOCKED: {KeyState.NORMAL, KeyState.DISABLED},
        KeyState.DISABLED: {KeyState.NORMAL}
    }
    
    def __init__(self):
        """KeyStateManager 클래스를 초기화합니다."""
        self._state = KeyState.NORMAL
        self._previous_states: list[KeyState] = []  # 상태 이력
        self._state_change_callbacks: Dict[KeyState, Set[Callable[[KeyState], None]]] = {
            state: set() for state in KeyState
        }
        
    @property
    def state(self) -> KeyState:
        """현재 키의 상태를 반환합니다."""
        return self._state
        
    @property
    def previous_state(self) -> Optional[KeyState]:
        """이전 상태를 반환합니다."""
        return self._previous_states[-1] if self._previous_states else None
        
    def can_transition_to(self, new_state: KeyState) -> bool:
        """특정 상태로 전이가 가능한지 확인합니다.
        
        Args:
            new_state (KeyState): 전이하고자 하는 상태
            
        Returns:
            bool: 전이 가능 여부
        """
        return new_state in self.VALID_TRANSITIONS[self._state]
        
    def set_state(self, new_state: KeyState) -> None:
        """키의 상태를 변경합니다.
        
        Args:
            new_state (KeyState): 변경할 새로운 상태
            
        Raises:
            InvalidStateTransitionError: 유효하지 않은 상태 전이 시도 시
        """
        if new_state == self._state:
            return
            
        if not self.can_transition_to(new_state):
            raise InvalidStateTransitionError(
                f"Invalid state transition: {self._state} -> {new_state}"
            )
            
        # 상태 이력 업데이트 (최대 10개까지만 저장)
        self._previous_states.append(self._state)
        if len(self._previous_states) > 10:
            self._previous_states.pop(0)
            
        # 상태 변경
        old_state = self._state
        self._state = new_state
        
        # 콜백 호출
        self._notify_state_change(old_state, new_state)
        
    def add_state_change_callback(self, state: KeyState, 
                                callback: Callable[[KeyState], None]) -> None:
        """특정 상태로 변경될 때 호출될 콜백을 등록합니다.
        
        Args:
            state (KeyState): 감시할 상태
            callback (Callable[[KeyState], None]): 호출될 콜백 함수
        """
        self._state_change_callbacks[state].add(callback)
        
    def remove_state_change_callback(self, state: KeyState,
                                   callback: Callable[[KeyState], None]) -> None:
        """등록된 상태 변경 콜백을 제거합니다.
        
        Args:
            state (KeyState): 감시 중인 상태
            callback (Callable[[KeyState], None]): 제거할 콜백 함수
        """
        self._state_change_callbacks[state].discard(callback)
        
    def _notify_state_change(self, old_state: KeyState, new_state: KeyState) -> None:
        """상태 변경을 구독자들에게 알립니다.
        
        Args:
            old_state (KeyState): 이전 상태
            new_state (KeyState): 새로운 상태
        """
        # 이전 상태의 콜백들 호출
        for callback in self._state_change_callbacks[old_state]:
            callback(new_state)
        # 새로운 상태의 콜백들 호출
        for callback in self._state_change_callbacks[new_state]:
            callback(old_state)
        
    def is_active(self) -> bool:
        """키가 활성 상태인지 확인합니다."""
        return self._state != KeyState.DISABLED
        
    def is_locked(self) -> bool:
        """키가 고정 상태인지 확인합니다."""
        return self._state == KeyState.LOCKED
        
    def disable(self) -> None:
        """키를 비활성화합니다."""
        self.set_state(KeyState.DISABLED)
        
    def enable(self) -> None:
        """키를 활성화합니다."""
        if self._state == KeyState.DISABLED:
            self.set_state(KeyState.NORMAL) 