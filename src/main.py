"""
날개 프로그램의 메인 진입점.
기본 애플리케이션 설정과 메인 윈도우를 초기화합니다.
"""

import sys
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QWidget,
    QVBoxLayout
)

from utils.logger import logger
from utils.config import config

class NalgaeWindow(QMainWindow):
    """날개 프로그램의 메인 윈도우"""
    
    def __init__(self):
        """메인 윈도우를 초기화합니다."""
        super().__init__()
        
        # 윈도우 기본 설정
        self.setWindowTitle("날개")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 타이틀바 제거
            Qt.WindowType.WindowStaysOnTopHint |  # 항상 위에 표시
            Qt.WindowType.Tool  # 작업 표시줄에서 숨김
        )
        
        # 크기 및 위치 설정
        self.resize(
            config.get("window.width", 1100),
            config.get("window.height", 450)
        )
        self.center()
        
        # 투명도 설정
        self.setWindowOpacity(config.get("window.opacity", 0.9))
        
        # 중앙 위젯 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # 시스템 트레이 아이콘 설정
        self._setup_system_tray()
        
        logger.info("메인 윈도우가 초기화되었습니다.")
    
    def _setup_system_tray(self):
        """시스템 트레이 아이콘과 메뉴를 설정합니다."""
        # 시스템 트레이 아이콘 생성
        self.tray_icon = QSystemTrayIcon(self)
        
        # 아이콘 이미지 설정 (나중에 실제 아이콘으로 교체 필요)
        # self.tray_icon.setIcon(QIcon("assets/icons/tray_icon.png"))
        
        # 트레이 메뉴 생성
        tray_menu = QMenu()
        
        # 종료 액션 추가
        quit_action = QAction("종료", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        # 메뉴를 트레이 아이콘에 설정
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def center(self):
        """윈도우를 화면 중앙에 위치시킵니다."""
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트를 처리합니다."""
        self._drag_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        """마우스 드래그 이벤트를 처리합니다."""
        if hasattr(self, '_drag_pos'):
            diff = event.globalPosition().toPoint() - self._drag_pos
            new_pos = self.pos() + QPoint(int(diff.x()), int(diff.y()))
            self.move(new_pos)
            self._drag_pos = event.globalPosition().toPoint()

def exception_hook(exctype, value, tb):
    """예외 처리 훅"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logger.error(f"예외 발생:\n{error_msg}")
    sys.__excepthook__(exctype, value, tb)

def main():
    """프로그램의 메인 진입점"""
    try:
        # 전역 예외 처리기 설정
        sys.excepthook = exception_hook
        
        # Qt 애플리케이션 생성
        app = QApplication(sys.argv)
        
        # 메인 윈도우 생성 및 표시
        window = NalgaeWindow()
        window.show()
        
        logger.info("프로그램이 시작되었습니다.")
        
        # 이벤트 루프 시작
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"프로그램 실행 중 치명적 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
