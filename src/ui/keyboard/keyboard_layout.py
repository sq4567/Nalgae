from PySide6.QtWidgets import QWidget, QPushButton, QApplication
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from utils.win32_utils import is_hangul_mode, switch_keyboard_layout
from core.input import send_key, SPECIAL_KEYS
from typing import Dict
import win32api
import win32con
import ctypes
from ctypes import wintypes


class KeyboardLayout(QWidget):
    """키보드 레이아웃 위젯
    
    기본 QWERTY 자판 배열을 구현합니다.
    레이아웃 매니저를 사용하지 않고 절대 위치로 버튼을 배치합니다.
    """
    
    key_pressed = Signal(str)  # 키 입력 시그널
    quit_requested = Signal()  # 종료 시그널
    
    # 한글/영문 키 매핑
    KEY_MAPPINGS: Dict[str, str] = {
        'Q': 'ㅂ', 'W': 'ㅈ', 'E': 'ㄷ', 'R': 'ㄱ', 'T': 'ㅅ',
        'Y': 'ㅛ', 'U': 'ㅕ', 'I': 'ㅑ', 'O': 'ㅐ', 'P': 'ㅔ',
        'A': 'ㅁ', 'S': 'ㄴ', 'D': 'ㅇ', 'F': 'ㄹ', 'G': 'ㅎ',
        'H': 'ㅗ', 'J': 'ㅓ', 'K': 'ㅏ', 'L': 'ㅣ',
        'Z': 'ㅋ', 'X': 'ㅌ', 'C': 'ㅊ', 'V': 'ㅍ', 'B': 'ㅠ',
        'N': 'ㅜ', 'M': 'ㅡ'
    }
    
    # 한글/영문 키 매핑
    SHIFT_KEY_MAPPINGS: Dict[str, str] = {
        '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
        '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
        '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
        ';': ':', '\'': '"', ',': '<', '.': '>', '/': '?',
        '`': '~'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 기본 단위 크기 설정
        self.unit_width = 50  # 기본 키의 너비
        self.unit_height = 50  # 기본 키의 높이
        
        # 키 폰트 설정
        self.key_font = QFont("KoPubWorldDotum Bold", 12)
        
        # 현재 버튼 저장을 위한 딕셔너리
        self.key_buttons: Dict[str, QPushButton] = {}
        
        # 특수 키 상태 저장
        self.special_key_states = {
            'Shift': False,
            'Ctrl': False,
            'Win': False,
            'Alt': False
        }
        
        # 현재 한/영 상태 저장
        self.is_hangul = is_hangul_mode()
        
        self._init_keyboard()
        self._update_hangul_button_label()  # 한영 버튼 라벨 업데이트
        self._update_key_labels()  # 키 라벨 업데이트
    
    def _update_hangul_button_label(self):
        """한영 버튼의 라벨을 현재 IME 상태에 맞게 업데이트합니다."""
        self.is_hangul = is_hangul_mode()  # 현재 IME 상태 확인
        self.hangul_btn.setText('한글' if self.is_hangul else 'ENG')
    
    def _update_key_labels(self):
        """키보드 키의 라벨을 IME 상태와 Shift 상태에 맞게 업데이트합니다."""
        shift_pressed = self.special_key_states['Shift']
        
        # 특수 키 목록 (텍스트가 변경되지 않아야 하는 키들)
        special_keys = {'ESC', 'Tab', 'Caps', 'Ctrl', 'Win', 'Alt', 'Enter', 
                       'Shift', 'Backspace', 'Del', 'Home', 'End', 'PageUp', 
                       'PageDn', 'Space'}  # Space 키 추가
        
        for key, btn in self.key_buttons.items():
            if key in special_keys:
                # 특수 키는 텍스트 변경하지 않음
                continue
            elif shift_pressed and key in self.SHIFT_KEY_MAPPINGS:
                # Shift가 눌린 상태에서는 특수문자로 표시
                btn.setText(self.SHIFT_KEY_MAPPINGS[key])
            elif key in self.KEY_MAPPINGS:
                # 한/영 상태에 따라 표시
                btn.setText(self.KEY_MAPPINGS[key] if self.is_hangul else key)
            elif key.isalpha():  # 알파벳의 경우
                btn.setText(key.upper() if shift_pressed else key.lower())
    
    def _init_keyboard(self):
        """키보드 레이아웃 초기화 - 절대 위치 사용"""
        # 첫 번째 행: ESC, 숫자 키들
        self._add_key('ESC', 0, 0)
        x_pos = 1  # 백틱 키를 추가할 위치
        self._add_key('`', x_pos, 0)  # 백틱 키 추가
        x_pos += 1  # 다음 키 위치로 이동
        for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=']:
            self._add_key(key, x_pos, 0)
            x_pos += 1
        
        # 백스페이스 키 추가
        backspace_btn = self._add_key('Backspace', x_pos, 0, width_units=1.5)
        backspace_btn.setText('←')  # 백스페이스 기호로 표시
        self.key_buttons['Backspace'] = backspace_btn
        
        # 종료 버튼 (임시 위치에 생성, adjust_window_size에서 최종 위치 조정)
        quit_btn = QPushButton('×', self)
        quit_btn.setGeometry(0, 0, 30, 30)  # 임시 위치
        quit_btn.clicked.connect(self.quit_requested.emit)
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #bc0000;
                border: none;
                color: white;
                font-size: 20px;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: #ff0000;
                color: white;
            }
        """)
        
        # 두 번째 행: Tab, QWERTY
        self._add_key('Tab', 0, 1, width_units=1.5)
        x_pos = 1.5
        for key in ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\']:
            self._add_key(key, x_pos, 1)
            x_pos += 1
        
        # Del 키 추가
        self._add_key('Del', x_pos, 1)
        
        # 세 번째 행: Caps Lock, ASDF
        self._add_key('Caps', 0, 2, width_units=1.75)
        x_pos = 1.75
        for key in ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'']:
            self._add_key(key, x_pos, 2)
            x_pos += 1
        self._add_key('Enter', x_pos, 2, width_units=1.75)
        
        # 네 번째 행: Shift, ZXCV
        self._add_key('Shift', 0, 3, width_units=2.25)
        x_pos = 2.25
        for key in ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/']:
            self._add_key(key, x_pos, 3)
            x_pos += 1
        self._add_key('Shift', x_pos, 3, width_units=2.25)
        
        # 다섯 번째 행: Ctrl, Win, Alt, 한자, Space, 한/영
        x_pos = 0
        for key, width in [('Ctrl', 1.25), ('Win', 1.25), ('Alt', 1.25)]:
            self._add_key(key, x_pos, 4, width_units=width)
            x_pos += width
        
        # 한자 키를 추가
        self.hanja_btn = self._add_key('한자', x_pos, 4, width_units=1.25)
        x_pos += 1.25
        
        # 스페이스바 (너비 조정)
        self._add_key('Space', x_pos, 4, width_units=5.0)
        x_pos += 5.0
        
        # 한영 키를 스페이스바 우측에 추가
        self.hangul_btn = self._add_key('한/영', x_pos, 4, width_units=1.25)
        x_pos += 1.25
        
        # 방향키 위치 및 크기 설정
        arrow_keys = {
            '↑': (17, 3),  # x좌표를 0.5 증가 (5픽셀 우측 이동)
            '←': (16, 4),  # x좌표를 0.5 증가
            '↓': (17, 4),  # x좌표를 0.5 증가
            '→': (18, 4)   # x좌표를 0.5 증가
        }
        # 방향키 버튼 생성 및 이벤트 연결
        for key, (x, y) in arrow_keys.items():
            btn = QPushButton(key, self)
            btn.setFont(self.key_font)
            # 크기를 10% 줄임 (0.9를 곱함)
            btn.setGeometry(
                int(x * self.unit_width),
                int(y * self.unit_height),
                int(self.unit_width),
                int(self.unit_height)
            )
            btn.clicked.connect(lambda checked, k=key: self._handle_arrow_key(k))
            self.key_buttons[key] = btn

        
        # Home, End, PageUp, PageDn 키 추가 (방향키 위에 2x2 그리드로)
        nav_keys = {
            'Home': (16, 0),    # ↑ 키 위
            'End': (16, 1),     # ↑ 키 위 한칸
            'PageUp': (17, 0),  # ↑ 키 위
            'PageDn': (17, 1)   # ↑ 키 위 한칸
        }
        
        # 네비게이션 키 버튼 생성 및 이벤트 연결
        for key, (x, y) in nav_keys.items():
            btn = QPushButton(key, self)
            btn.setFont(self.key_font)
            btn.setGeometry(
                int(x * self.unit_width),
                int(y * self.unit_height),
                int(self.unit_width),
                int(self.unit_height)
            )
            btn.clicked.connect(lambda checked, k=key: self._handle_key_press(k))
            self.key_buttons[key] = btn
    
    def _add_key(self, key: str, x: int, y: int, width_units: float = 1.0, height_units: float = 1.0) -> QPushButton:
        """키 버튼 추가
        
        Args:
            key (str): 키 텍스트
            x (int): x 좌표 (unit_width 단위)
            y (int): y 좌표 (unit_height 단위)
            width_units (float): 너비 (unit_width의 배수)
            height_units (float): 높이 (unit_height의 배수)
            
        Returns:
            QPushButton: 생성된 버튼
        """
        btn = QPushButton(key, self)
        btn.setFont(self.key_font)
        
        # 절대 위치 및 크기 설정
        x_pos = x * self.unit_width
        y_pos = y * self.unit_height
        width = int(self.unit_width * width_units)
        height = int(self.unit_height * height_units)
        
        btn.setGeometry(x_pos, y_pos, width, height)
        
        # 특수 키 처리
        if key in self.special_key_states:
            btn.clicked.connect(lambda: self._toggle_special_key(key))
        # 한/영 키 특별 처리
        elif key == '한/영':
            btn.clicked.connect(self._toggle_hangul)
        else:
            # 일반 키 입력 이벤트 연결
            btn.clicked.connect(lambda: self._handle_key_press(key))
        
        # 버튼 저장
        self.key_buttons[key] = btn
        
        return btn
    
    def _handle_key_press(self, key: str):
        """키 입력 처리"""
        
        # Home, End, PageUp, PageDn 키 처리
        if key in ['Home', 'End', 'PageUp', 'PageDn']:
            vk_code = SPECIAL_KEYS[key]
            win32api.keybd_event(vk_code, 0, 0, 0)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            return
    
        # Del 키 처리
        if key == 'Del':
            win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
            win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
            return
            
        # 특수 키가 눌려있는 상태라면 해당 키와 함께 처리
        if any(self.special_key_states.values()):
            # 키 입력 전송
            send_key(key)
            # 특수 키 해제
            self._release_special_keys()
            return
        
        # ESC 키 처리
        if key == 'ESC':
            win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
            win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
            return
        
        # Caps 키 처리
        if key == 'Caps':
            win32api.keybd_event(win32con.VK_CAPITAL, 0, 0, 0)
            win32api.keybd_event(win32con.VK_CAPITAL, 0, win32con.KEYEVENTF_KEYUP, 0)
            return
        
        # 백틱 키 처리
        if key == '`':
            win32api.keybd_event(0xC0, 0, 0, 0)  # 백틱 키 누름
            win32api.keybd_event(0xC0, 0, win32con.KEYEVENTF_KEYUP, 0)  # 백틱 키 뗌
            return
        
        # 한자 키 처리
        if key == '한자':
            win32api.keybd_event(win32con.VK_HANJA, 0, 0, 0)
            win32api.keybd_event(win32con.VK_HANJA, 0, win32con.KEYEVENTF_KEYUP, 0)
            return
        
        # 백스페이스 키 처리
        if key == 'Backspace':
            win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
            win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
            return
        
        # 특수 문자 키 처리
        special_char_mapping = {
            '1': (0x31, True),  # !
            '2': (0x32, True),  # @
            '3': (0x33, True),  # #
            '4': (0x34, True),  # $
            '5': (0x35, True),  # %
            '6': (0x36, True),  # ^
            '7': (0x37, True),  # &
            '8': (0x38, True),  # *
            '9': (0x39, True),  # (
            '0': (0x30, True),  # )
            '-': (0xBD, False),  # 하이픈/언더스코어 키
            '=': (0xBB, False),  # 등호/플러스 키
            '[': (0xDB, False),  # 왼쪽 대괄호
            ']': (0xDD, False),  # 오른쪽 대괄호
            '\\': (0xDC, False), # 백슬래시
            ';': (0xBA, False),  # 세미콜론
            '\'': (0xDE, False), # 작은따옴표
            ',': (0xBC, False),  # 쉼표
            '.': (0xBE, False),  # 마침표
            '/': (0xBF, False)   # 슬래시
        }
        
        if key in special_char_mapping:
            vk_code, need_shift = special_char_mapping[key]
            if need_shift:
                # Shift 키 누름 (필요한 경우)
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            # 해당 키 누름
            win32api.keybd_event(vk_code, 0, 0, 0)
            # 해당 키 뗌
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            if need_shift:
                # Shift 키 뗌 (필요한 경우)
                win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            return
        
        # 일반 키 입력 처리
        if key not in self.special_key_states:
            send_key(key)
            
            # 특수 키가 하나라도 pressed 상태 때
            if any(self.special_key_states.values()):
                self._release_special_keys()
    
    def _toggle_special_key(self, key: str):
        """특수 키 상태 토글 처리"""
        self.special_key_states[key] = not self.special_key_states[key]
        print(f"{key} 상태: {self.special_key_states[key]}")  # 상태 출력
        
        # 실제 키 입력 시뮬레이션
        if self.special_key_states[key]:
            # 키 누름 상태로
            win32api.keybd_event(SPECIAL_KEYS[key], 0, 0, 0)
        else:
            # 키 뗌
            win32api.keybd_event(SPECIAL_KEYS[key], 0, win32con.KEYEVENTF_KEYUP, 0)
        
        # Shift 키 상태가 변경되면 모든 키 라벨 업데이트
        if key == 'Shift':
            self._update_key_labels()  # Shift 키 상태에 따라 라벨 업데이트
            # Shift 키가 눌릴 때와 뗄 때 텍스트 전환
            for btn_key in self.SHIFT_KEY_MAPPINGS.keys():
                btn = self.key_buttons.get(btn_key)
                if btn:
                    if self.special_key_states['Shift']:
                        btn.setText(self.SHIFT_KEY_MAPPINGS[btn_key])  # 특수 문자로 변경
                    else:
                        btn.setText(btn_key)  # 원래 텍스트로 복원
    
    def _release_special_keys(self):
        """특수 키를 역순으로 해제"""
        needs_update = self.special_key_states['Shift']  # Shift 키가 눌려있었는지 확인
        
        for key in reversed(self.special_key_states.keys()):
            if self.special_key_states[key]:
                self.special_key_states[key] = False
                # 키 뗌
                win32api.keybd_event(SPECIAL_KEYS[key], 0, win32con.KEYEVENTF_KEYUP, 0)
                print(f"{key} 해제")  # 상태 출력
        
        # Shift 키가 해제되었다면 키 라벨 업데이트
        if needs_update:
            self._update_key_labels()  # Shift 키 상태에 따라 라벨 업데이트
            # Shift 키가 해제될 때 텍스트 복원
            for btn_key in self.SHIFT_KEY_MAPPINGS.keys():
                btn = self.key_buttons.get(btn_key)
                if btn:
                    btn.setText(btn_key)  # 원래 텍스트로 복원
    
    def _reset_special_keys(self):
        """모든 특수 키 상태 해제"""
        for key in self.special_key_states:
            self.special_key_states[key] = False
        print("모든 특수 키 상태 해제")  # 상태 출력
    
    def _toggle_hangul(self):
        """한/영 전환 버튼 클릭 처리"""
        # 한영 전환 수행
        switch_keyboard_layout()
        
        # IME 태 변경이 완료될 때지 잠시 대기
        QTimer.singleShot(50, self._update_after_ime_change)
    
    def _update_after_ime_change(self):
        """IME 상태 변경 후 UI 업데이트"""
        self._update_hangul_button_label()  # IME 상태에 따라 라벨 업데이트
        self._update_key_labels()  # 키 라벨 업데이트
    
    def _handle_arrow_key(self, key: str):
        """방향키 입력 처리"""
        key_mapping = {
            '↑': win32con.VK_UP,
            '↓': win32con.VK_DOWN, 
            '←': win32con.VK_LEFT,
            '→': win32con.VK_RIGHT
        }
        
        if key in key_mapping:
            vk_code = key_mapping[key]
            # 키 누름
            win32api.keybd_event(vk_code, 0, 0, 0)
            # 키 뗌 
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    def adjust_window_size(self):
        """모든 버튼들이 차지하는 최대 공간에 맞춰 크기를 조정합니다."""
        max_width = 0
        max_height = 0
        
        # 모든 버튼의 위치 및 크기를 계산하여 최대 크기 찾기
        for btn in self.key_buttons.values():
            btn_rect = btn.geometry()
            max_width = max(max_width, btn_rect.right())
            max_height = max(max_height, btn_rect.bottom())
        
        # 키보드 레이아웃 자체의 크기 설정
        self.setFixedSize(max_width, max_height)
        
        # 종료 버튼 위치 조정 (우상단 고정)
        quit_btn = [btn for btn in self.children() if isinstance(btn, QPushButton) and btn.text() == '×'][0]
        quit_btn.setGeometry(max_width - 30, 0, 30, 30)
        
        # MainWindow의 크기 조정
        if self.parent() and self.parent().parent():
            main_window = self.parent().parent()
            main_window.setFixedSize(max_width, max_height)

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002

class KEYBOARD_INPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBOARD_INPUT),
        ("padding", ctypes.c_byte * 8)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION)
    ]

def send_key_input(vk_code: int):
    """SendInput을 사용한 저수준 키 입력"""
    extra = ctypes.c_ulong(0)
    
    # 키 다운 이벤트
    input_down = INPUT(type=1)  # 1 = keyboard input
    input_down.union.ki = KEYBOARD_INPUT(
        wVk=vk_code,
        wScan=0,
        dwFlags=KEYEVENTF_KEYDOWN,
        time=0,
        dwExtraInfo=ctypes.pointer(extra)
    )
    
    # 키 업 이벤트
    input_up = INPUT(type=1)
    input_up.union.ki = KEYBOARD_INPUT(
        wVk=vk_code,
        wScan=0,
        dwFlags=KEYEVENTF_KEYUP,
        time=0,
        dwExtraInfo=ctypes.pointer(extra)
    )
    
    inputs = (INPUT * 2)(input_down, input_up)
    ctypes.windll.user32.SendInput(2, ctypes.pointer(inputs), ctypes.sizeof(INPUT))