"""키보드의 핵심 기능을 구현하는 모듈입니다."""

import logging
from typing import Dict, Optional, Tuple, Set, List
import time
import win32api
import win32con
from PySide6.QtGui import QColor
from functools import wraps
from dataclasses import dataclass
from datetime import datetime

from .key_state import KeyState, KeyStateManager, InvalidStateTransitionError
from .ime_manager import IMEState, IMEManager
from .key_label import KeyLabel, KeyLabelManager
from .key_simulator import KeySimulator
from .feedback_manager import FeedbackManager
from .memory_manager import MemoryManager

# 로거 설정
logger = logging.getLogger(__name__)

# 재시도 관련 상수
MAX_RETRY_COUNT = 3
RETRY_DELAY = 0.1  # seconds

# Health Check 관련 상수
HEALTH_CHECK_INTERVAL = 5.0  # seconds
MAX_ERROR_RATE = 0.1  # 10%
MAX_LATENCY = 0.1  # seconds

@dataclass
class KeyboardMetrics:
    """키보드 성능 메트릭을 저장하는 클래스입니다."""
    total_operations: int = 0
    failed_operations: int = 0
    total_latency: float = 0.0
    last_check_time: float = time.time()
    operation_history: List[Tuple[str, float, bool]] = None  # (operation, latency, success)
    
    def __post_init__(self):
        self.operation_history = []
        
    def add_operation(self, operation: str, latency: float, success: bool) -> None:
        """작업 결과를 기록합니다.
        
        Args:
            operation (str): 작업 종류
            latency (float): 작업 소요 시간
            success (bool): 작업 성공 여부
        """
        self.total_operations += 1
        self.total_latency += latency
        if not success:
            self.failed_operations += 1
        self.operation_history.append((operation, latency, success))
        
    def get_error_rate(self) -> float:
        """오류율을 계산합니다.
        
        Returns:
            float: 오류율 (0.0 ~ 1.0)
        """
        if self.total_operations == 0:
            return 0.0
        return self.failed_operations / self.total_operations
        
    def get_average_latency(self) -> float:
        """평균 지연 시간을 계산합니다.
        
        Returns:
            float: 평균 지연 시간(초)
        """
        if self.total_operations == 0:
            return 0.0
        return self.total_latency / self.total_operations
        
    def reset(self) -> None:
        """메트릭을 초기화합니다."""
        self.total_operations = 0
        self.failed_operations = 0
        self.total_latency = 0.0
        self.last_check_time = time.time()
        self.operation_history.clear()

def measure_performance(operation_name: str):
    """작업의 성능을 측정하는 데코레이터입니다.
    
    Args:
        operation_name (str): 작업 이름
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, '_metrics'):
                return func(self, *args, **kwargs)
                
            start_time = time.time()
            success = True
            try:
                result = func(self, *args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                latency = time.time() - start_time
                self._metrics.add_operation(operation_name, latency, success)
        return wrapper
    return decorator

def with_retry(max_retries: int = MAX_RETRY_COUNT, delay: float = RETRY_DELAY):
    """작업 실패 시 자동으로 재시도하는 데코레이터

    Args:
        max_retries (int): 최대 재시도 횟수
        delay (float): 재시도 간 대기 시간(초)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            logger.error(f"All {max_retries} attempts failed: {str(last_exception)}")
            raise last_exception
        return wrapper
    return decorator

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
        self._last_known_good_state = None
        
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
    
    def save_state(self) -> None:
        """현재 상태를 마지막으로 알려진 정상 상태로 저장합니다."""
        self._last_known_good_state = self.state
    
    def restore_state(self) -> None:
        """마지막으로 알려진 정상 상태로 복구합니다."""
        if self._last_known_good_state is not None:
            try:
                self._state_manager.set_state(self._last_known_good_state)
                logger.info(f"Key {self._key_code} restored to {self._last_known_good_state}")
            except InvalidStateTransitionError as e:
                logger.error(f"Failed to restore key {self._key_code}: {str(e)}")

    @with_retry()
    def press(self) -> None:
        """키를 누릅니다."""
        if not self._state_manager.is_active():
            return
            
        try:
            self.save_state()
            self._state_manager.set_state(KeyState.PRESSED)
            self._press_start_time = time.time()
        except InvalidStateTransitionError as e:
            logger.warning(f"Invalid key press attempt on key {self._key_code}")
            self.restore_state()
            raise e

    @with_retry()
    def release(self) -> None:
        """키를 뗍니다."""
        if not self._state_manager.is_active():
            return
            
        try:
            self.save_state()
            # 길게 누름 여부 확인
            if (self._press_start_time and 
                time.time() - self._press_start_time >= self._long_press_threshold):
                self._state_manager.set_state(KeyState.LOCKED)
            else:
                self._state_manager.set_state(KeyState.NORMAL)
                
            self._press_start_time = None
        except InvalidStateTransitionError as e:
            logger.warning(f"Invalid key release attempt on key {self._key_code}")
            self.restore_state()
            raise e
    
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
        self._feedback_manager = FeedbackManager()
        self._memory_manager = MemoryManager()
        self._active_function_keys: Set[str] = set()
        self._metrics = KeyboardMetrics()
        
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
            key = Key(key_id, label, is_function_key=is_function)
            self._keys[key_id] = key
            self._feedback_manager.initialize_key(key_id, key.color)
            
        # 알파벳 키 초기화
        for c in range(ord('a'), ord('z') + 1):
            char = chr(c)
            label = self._label_manager.create_label(char, char.upper())
            key = Key(char, label)
            self._keys[char] = key
            self._feedback_manager.initialize_key(char, key.color)
            
        # 숫자 키 초기화
        for num in range(10):
            num_str = str(num)
            label = self._label_manager.create_label(num_str, num_str)
            key = Key(num_str, label)
            self._keys[num_str] = key
            self._feedback_manager.initialize_key(num_str, key.color)
            
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
            key = Key(key_id, label)
            self._keys[key_id] = key
            self._feedback_manager.initialize_key(key_id, key.color)
            
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
        
    @measure_performance("mouse_move")
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
            
    @measure_performance("mouse_press")
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
            self._feedback_manager.play_key_press_sound(key_id)
            return
            
        # Caps Lock 키 처리
        if key_id == 'caps_lock':
            # 한글 모드에서는 영문 모드로 전환
            if self._ime_manager.is_korean():
                self._ime_manager.force_state(IMEState.ENGLISH)
            self._label_manager.toggle_caps_lock()
            self._feedback_manager.play_key_press_sound(key_id)
            return
            
        key.press()
        self._feedback_manager.play_key_press_sound(key_id)
        
        # 기능 키 상태 업데이트
        if key.is_function_key:
            self._update_function_keys(key_id, True)
        else:
            # 일반 키는 활성화된 기능 키들과 함께 시뮬레이션
            self._key_simulator.press_key(key_id)
            
    @measure_performance("mouse_release")
    def handle_mouse_release(self, key_id: str) -> None:
        """마우스 클릭 해제 이벤트를 처리합니다.
        
        Args:
            key_id (str): 해제된 키의 식별자
        """
        if key_id not in self._keys:
            return
            
        key = self._keys[key_id]
        key.release()
        
        # 모든 키에 대해 뗌 소리 재생
        self._feedback_manager.play_key_release_sound(key_id)
        
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
        
        # 메모리 정리
        self._memory_manager.cleanup_resources()
        
    @property
    def visual_feedback_enabled(self) -> bool:
        """시각적 피드백 활성화 여부를 반환합니다."""
        return self._feedback_manager.visual_enabled
        
    @visual_feedback_enabled.setter
    def visual_feedback_enabled(self, value: bool) -> None:
        """시각적 피드백 활성화 여부를 설정합니다."""
        self._feedback_manager.visual_enabled = value
        
    @property
    def sound_feedback_enabled(self) -> bool:
        """소리 피드백 활성화 여부를 반환합니다."""
        return self._feedback_manager.sound_enabled
        
    @sound_feedback_enabled.setter
    def sound_feedback_enabled(self, value: bool) -> None:
        """소리 피드백 활성화 여부를 설정합니다."""
        self._feedback_manager.sound_enabled = value
        
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
        
    def check_health(self) -> Tuple[bool, str]:
        """키보드의 상태를 점검합니다.
        
        Returns:
            Tuple[bool, str]: (정상 여부, 상태 메시지)
        """
        current_time = time.time()
        if current_time - self._metrics.last_check_time < HEALTH_CHECK_INTERVAL:
            return True, "Health check skipped (too frequent)"
            
        # 성능 메트릭 분석
        error_rate = self._metrics.get_error_rate()
        avg_latency = self._metrics.get_average_latency()
        
        issues = []
        
        # 오류율 검사
        if error_rate > MAX_ERROR_RATE:
            issues.append(f"High error rate: {error_rate:.1%}")
            
        # 지연 시간 검사
        if avg_latency > MAX_LATENCY:
            issues.append(f"High latency: {avg_latency*1000:.1f}ms")
            
        # 키 상태 검사
        inactive_keys = [key_id for key_id, key in self._keys.items() 
                        if not key.is_active()]
        if inactive_keys:
            issues.append(f"Inactive keys: {', '.join(inactive_keys)}")
            
        # IME 상태 검사
        if self._ime_manager._sync_failures > 0:
            issues.append(f"IME sync failures: {self._ime_manager._sync_failures}")
            
        # 메트릭 초기화
        self._metrics.reset()
        
        if issues:
            return False, " | ".join(issues)
        return True, "All systems operational"
        
    def get_performance_report(self) -> str:
        """성능 보고서를 생성합니다.
        
        Returns:
            str: 성능 보고서
        """
        report = ["Keyboard Performance Report", "=" * 30]
        
        # 기본 메트릭
        report.append(f"Total Operations: {self._metrics.total_operations}")
        report.append(f"Error Rate: {self._metrics.get_error_rate():.1%}")
        report.append(f"Average Latency: {self._metrics.get_average_latency()*1000:.1f}ms")
        
        # 작업별 통계
        op_stats = {}
        for op, latency, success in self._metrics.operation_history:
            if op not in op_stats:
                op_stats[op] = {"count": 0, "failures": 0, "total_latency": 0.0}
            op_stats[op]["count"] += 1
            op_stats[op]["total_latency"] += latency
            if not success:
                op_stats[op]["failures"] += 1
                
        report.append("\nOperation Statistics:")
        for op, stats in op_stats.items():
            avg_latency = stats["total_latency"] / stats["count"]
            error_rate = stats["failures"] / stats["count"]
            report.append(f"- {op}:")
            report.append(f"  Count: {stats['count']}")
            report.append(f"  Error Rate: {error_rate:.1%}")
            report.append(f"  Avg Latency: {avg_latency*1000:.1f}ms")
            
        # 메모리 사용 보고서 추가
        memory_report = self._memory_manager.get_memory_report()
        report = f"{report}\n\n{memory_report}"
        
        return "\n".join(report)
        
    def _get_cached_key_label(self, key_id: str) -> str:
        """캐시된 키 레이블을 가져옵니다."""
        # 캐시에서 레이블 확인
        cache_key = f"label_{key_id}"
        cached_label = self._memory_manager.cache_get(cache_key)
        
        if cached_label is not None:
            return cached_label
            
        # 캐시 미스: 레이블 생성 및 캐시 저장
        label = super().get_key_label(key_id)
        self._memory_manager.cache_set(cache_key, label)
        
        return label