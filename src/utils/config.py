"""
설정 관리 모듈.
프로그램의 전역 설정을 관리합니다.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import logger

class Config:
    """날개 프로그램의 설정을 관리하는 클래스"""
    
    def __init__(self):
        """설정 관리자를 초기화합니다."""
        self._config: Dict[str, Any] = {}
        self._config_file = Path("config/settings.json")
        self._load_default_config()
        self._load_config()
    
    def _load_default_config(self):
        """기본 설정값을 로드합니다."""
        self._config = {
            "window": {
                "always_on_top": True,
                "opacity": 0.9,
                "width": 800,
                "height": 400,
            },
            "keyboard": {
                "layout": "default",
                "theme": "default",
                "sound_enabled": True,
                "sound_volume": 0.5,
            },
            "accessibility": {
                "high_contrast": False,
                "key_size": "medium",
                "animation_speed": "normal",
            },
            "features": {
                "guide_enabled": True,
                "breeze_enabled": True,
                "warp_enabled": True,
                "transformation_enabled": True,
            }
        }
    
    def _load_config(self):
        """설정 파일에서 설정을 로드합니다."""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 기존 설정을 유저 설정으로 업데이트
                    self._update_nested_dict(self._config, user_config)
                    logger.info("설정 파일을 성공적으로 로드했습니다.")
            else:
                self._save_config()
                logger.info("기본 설정 파일을 생성했습니다.")
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류 발생: {e}")
    
    def _save_config(self):
        """현재 설정을 파일에 저장합니다."""
        try:
            # 설정 디렉토리가 없으면 생성
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            logger.info("설정을 파일에 저장했습니다.")
        except Exception as e:
            logger.error(f"설정 저장 중 오류 발생: {e}")
    
    def _update_nested_dict(self, d: dict, u: dict) -> dict:
        """중첩된 딕셔너리를 업데이트합니다."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값을 가져옵니다.
        
        Args:
            key (str): 설정 키 (예: "window.opacity")
            default: 키가 없을 경우 반환할 기본값
            
        Returns:
            설정값 또는 기본값
        """
        try:
            value = self._config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        설정값을 저장합니다.
        
        Args:
            key (str): 설정 키 (예: "window.opacity")
            value: 저장할 값
        """
        keys = key.split('.')
        current = self._config
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
        self._save_config()

# 전역 설정 인스턴스 생성
config = Config()
