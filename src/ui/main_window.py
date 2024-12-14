from PySide6.QtWidgets import QMainWindow, QWidget, QApplication, QStackedWidget, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.keyboard.keyboard_layout import KeyboardLayout
import win32gui
import win32con
from core.input import send_key


class MainWindow(QMainWindow):
    """메인 윈도우 클래스
    
    기본적인 화상키보드 윈도우를 구현합니다.
    항상 최상위에 표시되며, 프레임이 없는 윈도우 스타일을 가집니다.
    """
    
    def __init__(self):
        super().__init__()
        
        # 윈도우 기본 설정
        self.setWindowTitle("날개")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |  # 항상 위
            Qt.WindowType.FramelessWindowHint |    # 프레임 없음
            Qt.WindowType.Tool                     # 작업 표시줄에 표시 안 함
        )
        
        # WS_EX_NOACTIVATE 스타일 적용
        hwnd = self.winId().__int__()
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(
            hwnd, 
            win32con.GWL_EXSTYLE, 
            style | win32con.WS_EX_NOACTIVATE
        )
        
        # 중앙 위젯을 QStackedWidget으로 변경
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # 기본 폰트 설정
        self.setFont(QFont("KoPubWorldDotum Bold", 10))
        
        # UI 초기화
        self._init_ui()
        
        # 초기 크기는 키보드 레이아웃의 크기에 맞춰 자동 설정됨
    
    def _init_ui(self):
        """UI 컴포넌트 초기화"""
        # 일반 모드 키보드 레이아웃 생성
        self.normal_keyboard = KeyboardLayout(self)
        self.normal_keyboard.key_pressed.connect(self._on_key_pressed)
        self.normal_keyboard.quit_requested.connect(QApplication.quit)
        self.normal_keyboard.mode_changed.connect(self._on_mode_changed)
        
        # 날개 모드 키보드 레이아웃 생성
        self.nalgae_keyboard = NalgaeKeyboardLayout(self)
        self.nalgae_keyboard.key_pressed.connect(self._on_key_pressed)
        self.nalgae_keyboard.quit_requested.connect(QApplication.quit)
        self.nalgae_keyboard.mode_changed.connect(self._on_mode_changed)
        
        # 스택에 위젯 추가
        self.central_widget.addWidget(self.normal_keyboard)
        self.central_widget.addWidget(self.nalgae_keyboard)
        
        # 초기 크기 설정
        self.normal_keyboard.adjust_window_size()
    
    def _on_mode_changed(self):
        """모드 전환 처리"""
        current_index = self.central_widget.currentIndex()
        new_index = 1 if current_index == 0 else 0
        
        # 페이지 전환
        self.central_widget.setCurrentIndex(new_index)
        
        # 현재 표시된 키보드의 크기에 맞춰 창 크기 조정
        current_keyboard = self.central_widget.currentWidget()
        current_keyboard.adjust_window_size()
    
    def _on_key_pressed(self, key: str):
        """키 입력 처리"""
        send_key(key)
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 처리 - 윈도우 드래그 기능"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리 - 윈도우 드래그 기능"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class NalgaeKeyboardLayout(QWidget):
    key_pressed = Signal(str)
    quit_requested = Signal()
    mode_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.key_buttons = {}
        self.is_nalgae_mode = True
        self.unit_width = 50   # KeyboardLayout과 동일한 크기 사용
        self.unit_height = 50
        self._init_keyboard()

    def _init_keyboard(self):
        """키보드 레이아웃 초기화 - 절대 위치 사용"""
        
        # 3x3 버튼 생성 (간격 없이 붙여서 배치)
        for row in range(3):
            for col in range(3):
                btn = QPushButton(f"빝{row*3 + col + 1}", self)
                btn.setFixedSize(self.unit_width, self.unit_height)
                
                # 절대 위치로 버튼 배치
                x = col * self.unit_width
                y = row * self.unit_height
                btn.setGeometry(x, y, self.unit_width, self.unit_height)
                self.key_buttons[f"빝{row*3 + col + 1}"] = btn
                btn.clicked.connect(lambda checked, k=f"빝{row*3 + col + 1}": self.key_pressed.emit(k))

        # 종료 버튼과 모드 전환 버튼 추가 (기존 코드와 동일)
        self.quit_button = QPushButton('×', self)
        self.quit_button.clicked.connect(self.quit_requested.emit)
        self.quit_button.setStyleSheet("""
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
        
        # 모드 전환 버튼 추가
        self.mode_button = QPushButton('일', self)
        self.mode_button.clicked.connect(self._on_mode_button_clicked)
        self.mode_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                border: none;
                color: white;
                font-size: 16px;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background-color: #666666;
                color: white;
            }
        """)

    def _on_mode_button_clicked(self):
        self.mode_changed.emit()

    def adjust_window_size(self):
        """날개 모드에서의 창 크기 조정"""
        # 1. 키보드 버튼들의 영역 계산
        keyboard_width = 0
        keyboard_height = 0
        
        for btn in self.key_buttons.values():
            btn_rect = btn.geometry()
            keyboard_width = max(keyboard_width, btn_rect.right())
            keyboard_height = max(keyboard_height, btn_rect.bottom())
        
        # 2. 종료 버튼 너비(30px)를 네 모서리에 추가
        total_width = keyboard_width + (30 * 2)  # 좌우 각각 30px
        total_height = keyboard_height + (30 * 2)  # 상하 각각 30px
        
        # 3. 창 크기 조정 및 버튼 재배치
        self.setFixedSize(total_width, total_height)
        
        # 키보드 버튼들을 중앙으로 이동
        x_offset = 30  # 왼쪽 여백
        y_offset = 30  # 위쪽 여백
        
        for btn in self.key_buttons.values():
            current_pos = btn.geometry()
            btn.setGeometry(
                current_pos.x() + x_offset,
                current_pos.y() + y_offset,
                current_pos.width(),
                current_pos.height()
            )
        
        # 종료 버튼과 모드 전환 버튼 위치 설정
        # 우상단
        self.quit_button.setGeometry(total_width - 30, 0, 30, 30)
        self.mode_button.setGeometry(total_width - 30, 30, 30, 30)
        
        # MainWindow 크기 조정
        if self.parent() and self.parent().parent():
            main_window = self.parent().parent()
            main_window.setFixedSize(total_width, total_height)
