"""
로깅 유틸리티 모듈.
프로그램 전반에 걸쳐 일관된 로깅을 제공합니다.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

class NalgaeLogger:
    """날개 프로그램의 로깅을 담당하는 클래스"""
    
    def __init__(self, name: str = "nalgae"):
        """
        로거를 초기화합니다.

        Args:
            name (str): 로거의 이름. 기본값은 "nalgae".
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 로그 디렉토리 생성
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 파일명에 날짜 포함
        current_date = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"nalgae_{current_date}.log"
        
        # 파일 핸들러 설정 (최대 5MB, 백업 5개)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """디버그 레벨 로그를 기록합니다."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """정보 레벨 로그를 기록합니다."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """경고 레벨 로그를 기록합니다."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """에러 레벨 로그를 기록합니다."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """치명적 에러 레벨 로그를 기록합니다."""
        self.logger.critical(message)

# 전역 로거 인스턴스 생성
logger = NalgaeLogger()
