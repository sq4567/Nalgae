"""키보드의 메모리 관리를 담당하는 모듈입니다."""

import logging
import psutil
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# 메모리 관련 상수
MAX_CACHE_SIZE = 1000  # 최대 캐시 항목 수
CACHE_CLEANUP_THRESHOLD = 0.8  # 캐시 정리 임계값 (80%)
MEMORY_WARNING_THRESHOLD = 0.85  # 메모리 경고 임계값 (85%)
RESOURCE_CLEANUP_INTERVAL = 300  # 리소스 정리 주기 (5분)

@dataclass
class CacheItem:
    """캐시 항목을 나타내는 클래스입니다."""
    value: Any
    last_access: float
    access_count: int = 0

class MemoryManager:
    """키보드의 메모리 사용을 관리하는 클래스입니다."""
    
    def __init__(self):
        """MemoryManager 클래스를 초기화합니다."""
        self._cache: Dict[str, CacheItem] = {}
        self._last_cleanup_time = time.time()
        self._process = psutil.Process()
        
    def get_memory_usage(self) -> float:
        """현재 프로세스의 메모리 사용량을 반환합니다.
        
        Returns:
            float: 메모리 사용량 (MB)
        """
        return self._process.memory_info().rss / 1024 / 1024
        
    def check_memory_status(self) -> tuple[bool, str]:
        """메모리 상태를 점검합니다.
        
        Returns:
            tuple[bool, str]: (정상 여부, 상태 메시지)
        """
        memory_usage = self.get_memory_usage()
        system_memory = psutil.virtual_memory()
        
        # 시스템 메모리 사용률 계산
        memory_percent = system_memory.percent / 100
        
        if memory_percent > MEMORY_WARNING_THRESHOLD:
            return False, f"High memory usage: {memory_percent:.1%}"
            
        # 캐시 크기 확인
        if len(self._cache) > MAX_CACHE_SIZE * CACHE_CLEANUP_THRESHOLD:
            return False, f"Cache near capacity: {len(self._cache)}/{MAX_CACHE_SIZE}"
            
        return True, f"Memory usage: {memory_usage:.1f}MB ({memory_percent:.1%})"
        
    def cleanup_resources(self) -> None:
        """주기적으로 리소스를 정리합니다."""
        current_time = time.time()
        
        # 정리 주기 확인
        if current_time - self._last_cleanup_time < RESOURCE_CLEANUP_INTERVAL:
            return
            
        logger.info("Starting resource cleanup...")
        
        # 캐시 정리
        self._cleanup_cache()
        
        # 가비지 컬렉션 강제 실행
        import gc
        gc.collect()
        
        self._last_cleanup_time = current_time
        logger.info("Resource cleanup completed")
        
    def _cleanup_cache(self) -> None:
        """캐시를 정리합니다."""
        if len(self._cache) <= MAX_CACHE_SIZE * CACHE_CLEANUP_THRESHOLD:
            return
            
        # 접근 빈도와 최근 접근 시간을 기준으로 정렬
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: (x[1].access_count, x[1].last_access)
        )
        
        # 하위 20% 항목 제거
        items_to_remove = int(len(self._cache) * 0.2)
        for key, _ in sorted_items[:items_to_remove]:
            del self._cache[key]
            
        logger.debug(f"Removed {items_to_remove} items from cache")
        
    def cache_get(self, key: str) -> Optional[Any]:
        """캐시에서 값을 가져옵니다.
        
        Args:
            key (str): 캐시 키
            
        Returns:
            Optional[Any]: 캐시된 값 또는 None
        """
        if key in self._cache:
            item = self._cache[key]
            item.last_access = time.time()
            item.access_count += 1
            return item.value
        return None
        
    def cache_set(self, key: str, value: Any) -> None:
        """캐시에 값을 저장합니다.
        
        Args:
            key (str): 캐시 키
            value (Any): 저장할 값
        """
        # 캐시가 가득 찼는지 확인
        if len(self._cache) >= MAX_CACHE_SIZE:
            self._cleanup_cache()
            
        self._cache[key] = CacheItem(
            value=value,
            last_access=time.time()
        )
        
    def get_memory_report(self) -> str:
        """메모리 사용 보고서를 생성합니다.
        
        Returns:
            str: 메모리 사용 보고서
        """
        memory_usage = self.get_memory_usage()
        system_memory = psutil.virtual_memory()
        
        report = [
            "=== Memory Usage Report ===",
            f"Time: {datetime.now()}",
            f"Process Memory: {memory_usage:.1f}MB",
            f"System Memory: {system_memory.percent}%",
            f"Cache Items: {len(self._cache)}",
            f"Last Cleanup: {datetime.fromtimestamp(self._last_cleanup_time)}"
        ]
        
        return "\n".join(report) 