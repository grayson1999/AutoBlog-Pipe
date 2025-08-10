"""
고급 로깅 시스템
파일 로깅, 로그 로테이션, 성능 모니터링 지원
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import functools
import time

try:
    from ..config import Config
except ImportError:
    # 직접 실행 시를 위한 fallback
    Config = None


class AutoBlogLogger:
    """AutoBlog-Pipe 전용 로깅 시스템"""
    
    def __init__(self, log_level: str = "INFO"):
        """
        로거 초기화
        
        Args:
            log_level (str): 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 로거 설정
        self.logger = logging.getLogger("AutoBlogPipe")
        self.logger.setLevel(self.log_level)
        
        # 기존 핸들러 제거 (중복 방지)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        self._setup_file_handler()
        self._setup_console_handler()
        self._setup_error_handler()
        
        # 성능 측정용
        self._start_times = {}
        
        self.logger.info("AutoBlogLogger initialized successfully")
    
    def _setup_file_handler(self):
        """파일 핸들러 설정 (로그 로테이션 포함)"""
        log_file = self.log_dir / "autoblog.log"
        
        # 로테이팅 파일 핸들러 (최대 5MB, 백업 5개)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """콘솔 핸들러 설정"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Windows 호환성을 위해 UTF-8 인코딩 강제 설정 시도
        try:
            console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, UnicodeError):
            # 이전 Python 버전이나 설정이 안 되는 경우 패스
            pass
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.log_level)
        
        self.logger.addHandler(console_handler)
    
    def _setup_error_handler(self):
        """에러 전용 핸들러 설정"""
        error_file = self.log_dir / "errors.log"
        
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=2*1024*1024,  # 2MB
            backupCount=3,
            encoding='utf-8'
        )
        
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s\n%(exc_info)s'
        )
        error_handler.setFormatter(error_formatter)
        error_handler.setLevel(logging.ERROR)
        
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """DEBUG 레벨 로그"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """INFO 레벨 로그"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """WARNING 레벨 로그"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """ERROR 레벨 로그"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=exception, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """CRITICAL 레벨 로그"""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", exc_info=exception, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)
    
    def log_pipeline_start(self, mode: str, **params):
        """파이프라인 시작 로그"""
        self.info(f"[PIPELINE] Started: mode={mode}", extra={"mode": mode, **params})
        self._start_times['pipeline'] = time.time()
    
    def log_pipeline_end(self, result: Dict[str, Any]):
        """파이프라인 완료 로그"""
        duration = time.time() - self._start_times.get('pipeline', time.time())
        success_rate = (result.get('success_count', 0) / result.get('total_count', 1)) * 100
        
        self.info(
            f"[PIPELINE] Completed: {result.get('success_count', 0)}/{result.get('total_count', 0)} posts "
            f"({success_rate:.1f}% success) in {duration:.1f}s",
            extra={
                "success_count": result.get('success_count', 0),
                "total_count": result.get('total_count', 0),
                "success_rate": success_rate,
                "duration": duration
            }
        )
    
    def log_post_generation(self, title: str, success: bool, duration: Optional[float] = None):
        """포스트 생성 로그"""
        status = "[SUCCESS]" if success else "[FAILED]"
        duration_str = f" ({duration:.1f}s)" if duration else ""
        
        if success:
            self.info(f"{status} Generated: {title}{duration_str}", extra={"title": title, "duration": duration})
        else:
            self.warning(f"{status} Generation: {title}{duration_str}", extra={"title": title, "duration": duration})
    
    def log_api_call(self, api_name: str, success: bool, duration: float, **details):
        """API 호출 로그"""
        status = "[SUCCESS]" if success else "[FAILED]"
        self.info(
            f"{status} {api_name} API: {duration:.1f}s",
            extra={"api": api_name, "success": success, "duration": duration, **details}
        )
    
    def log_duplicate_skip(self, title: str, similarity: float):
        """중복 스킵 로그"""
        self.warning(
            f"[DUPLICATE] Skipped: '{title}' (similarity: {similarity:.2%})",
            extra={"title": title, "similarity": similarity}
        )
    
    def log_commit_push(self, file_path: str, commit_hash: str, success: bool):
        """Git 커밋/푸시 로그"""
        if success:
            self.info(
                f"[GIT] Push successful: {Path(file_path).name} -> {commit_hash[:8]}",
                extra={"file": file_path, "commit": commit_hash}
            )
        else:
            self.error(
                f"[GIT] Push failed: {Path(file_path).name}",
                extra={"file": file_path}
            )
    
    def get_log_stats(self) -> Dict[str, Any]:
        """로그 통계 반환"""
        stats = {
            "log_dir": str(self.log_dir),
            "log_files": [],
            "total_size": 0
        }
        
        try:
            for log_file in self.log_dir.glob("*.log*"):
                file_size = log_file.stat().st_size
                stats["log_files"].append({
                    "name": log_file.name,
                    "size": file_size,
                    "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                })
                stats["total_size"] += file_size
            
            stats["log_files"].sort(key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            self.error("Failed to get log stats", e)
        
        return stats


def timed_operation(operation_name: str):
    """성능 측정 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"[TIMER] {operation_name} completed in {duration:.2f}s")
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[TIMER] {operation_name} failed after {duration:.2f}s", exception=e)
                raise
        
        return wrapper
    return decorator


def api_call_logger(api_name: str):
    """API 호출 로깅 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_api_call(api_name, True, duration)
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                logger.log_api_call(api_name, False, duration, error=str(e))
                raise
        
        return wrapper
    return decorator


# 글로벌 로거 인스턴스
_global_logger: Optional[AutoBlogLogger] = None


def get_logger() -> AutoBlogLogger:
    """글로벌 로거 인스턴스 반환"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AutoBlogLogger()
    return _global_logger


def setup_logging(log_level: str = "INFO"):
    """로깅 시스템 초기화"""
    global _global_logger
    _global_logger = AutoBlogLogger(log_level)
    return _global_logger


def test_logger():
    """로거 테스트 함수"""
    try:
        logger = setup_logging("DEBUG")
        
        logger.info("[TEST] Testing AutoBlogLogger...")
        
        # 기본 로그 레벨 테스트
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        
        # 예외 로깅 테스트
        try:
            raise ValueError("Test exception")
        except Exception as e:
            logger.error("Error message test", exception=e)
        
        # 성능 로깅 테스트
        logger.log_pipeline_start("test", count=1)
        time.sleep(0.1)  # 시뮬레이션
        logger.log_pipeline_end({"success_count": 1, "total_count": 1})
        
        # 포스트 생성 로깅 테스트
        logger.log_post_generation("Test Post", True, 2.5)
        logger.log_duplicate_skip("Duplicate Post", 0.85)
        
        # API 호출 로깅 테스트
        logger.log_api_call("OpenAI", True, 1.2, tokens=150)
        
        # 통계 확인
        stats = logger.get_log_stats()
        logger.info(f"[STATS] Log stats: {stats['total_size']} bytes in {len(stats['log_files'])} files")
        
        print("[SUCCESS] Logger test completed successfully!")
        print(f"[INFO] Log files created in: {logger.log_dir}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Logger test failed: {e}")
        return False


if __name__ == "__main__":
    test_logger()