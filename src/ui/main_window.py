from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.keyboard.keyboard_layout import KeyboardLayout
from core.input import send_key
import win32gui
import win32con


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
        
        # 중앙 위젯 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 기본 폰트 설정
        self.setFont(QFont("KoPubWorldDotum Bold", 10))
        
        # UI 초기화 (키보드 레이아웃 생성)
        self._init_ui()
        
        # 초기 크기는 키보드 레이아웃의 크기에 맞춰 자동 설정됨
    
    def _init_ui(self):
        """UI 컴포넌트 초기화"""
        # 키보드 레이아웃 생성
        self.keyboard = KeyboardLayout(self.central_widget)
        
        # 키 입력 이벤트 연결
        self.keyboard.key_pressed.connect(self._on_key_pressed)
        # 종료 이벤트 연결
        self.keyboard.quit_requested.connect(QApplication.quit)
        
        # 키보드 레이아웃 크기에 맞춰 창 크기 조정
        self.keyboard.adjust_window_size()
    
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
