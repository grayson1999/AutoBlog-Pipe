"""
고급 예외 처리 및 복구 시스템
API 한도, 네트워크 장애, 빌드 실패 등 다양한 예외 상황 처리
"""

import time
import traceback
from typing import Callable, Any, Optional, Dict
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import openai
from openai import OpenAI

try:
    from .logger import get_logger
except ImportError:
    # 직접 실행 시 fallback
    def get_logger():
        import logging
        return logging.getLogger(__name__)


class RetryConfig:
    """재시도 설정"""
    
    # OpenAI API 재시도 설정
    OPENAI_MAX_RETRIES = 3
    OPENAI_RETRY_DELAYS = [1, 2, 4]  # 지수 백오프
    OPENAI_RETRY_ERRORS = [
        "rate_limit_exceeded",
        "server_error", 
        "timeout",
        "connection_error"
    ]
    
    # HTTP 요청 재시도 설정
    HTTP_MAX_RETRIES = 3
    HTTP_BACKOFF_FACTOR = 0.3
    HTTP_STATUS_FORCELIST = [500, 502, 503, 504]
    
    # Git 작업 재시도 설정
    GIT_MAX_RETRIES = 2
    GIT_RETRY_DELAY = 2


class APIError(Exception):
    """API 관련 예외"""
    def __init__(self, message: str, error_type: str = "unknown", retry_after: Optional[int] = None):
        super().__init__(message)
        self.error_type = error_type
        self.retry_after = retry_after


class NetworkError(Exception):
    """네트워크 관련 예외"""
    pass


class ContentGenerationError(Exception):
    """콘텐츠 생성 관련 예외"""
    pass


class GitOperationError(Exception):
    """Git 작업 관련 예외"""
    pass


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """재시도 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"[RETRY] Final attempt failed for {func.__name__}: {str(e)}")
                        raise
                    
                    wait_time = delay * (backoff_factor ** attempt)
                    logger.warning(f"[RETRY] Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}")
                    logger.info(f"[RETRY] Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
            
            return None  # 실제로는 도달하지 않음
        
        return wrapper
    return decorator


def handle_openai_errors(func: Callable) -> Callable:
    """OpenAI API 에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger()
        
        for attempt in range(RetryConfig.OPENAI_MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            
            except openai.RateLimitError as e:
                if attempt == RetryConfig.OPENAI_MAX_RETRIES - 1:
                    logger.error(f"[API] OpenAI rate limit exceeded - final attempt failed: {str(e)}")
                    raise APIError(f"OpenAI rate limit exceeded: {str(e)}", "rate_limit_exceeded")
                
                # Rate limit 정보 파싱
                retry_after = getattr(e, 'retry_after', None) or RetryConfig.OPENAI_RETRY_DELAYS[attempt]
                logger.warning(f"[API] Rate limit hit, waiting {retry_after}s before retry {attempt + 1}/{RetryConfig.OPENAI_MAX_RETRIES}")
                time.sleep(retry_after)
            
            except openai.APIError as e:
                if attempt == RetryConfig.OPENAI_MAX_RETRIES - 1:
                    logger.error(f"[API] OpenAI API error - final attempt failed: {str(e)}")
                    raise APIError(f"OpenAI API error: {str(e)}", "api_error")
                
                logger.warning(f"[API] API error, retrying {attempt + 1}/{RetryConfig.OPENAI_MAX_RETRIES}: {str(e)}")
                time.sleep(RetryConfig.OPENAI_RETRY_DELAYS[attempt])
            
            except openai.APIConnectionError as e:
                if attempt == RetryConfig.OPENAI_MAX_RETRIES - 1:
                    logger.error(f"[API] OpenAI connection error - final attempt failed: {str(e)}")
                    raise APIError(f"OpenAI connection error: {str(e)}", "connection_error")
                
                logger.warning(f"[API] Connection error, retrying {attempt + 1}/{RetryConfig.OPENAI_MAX_RETRIES}: {str(e)}")
                time.sleep(RetryConfig.OPENAI_RETRY_DELAYS[attempt])
            
            except openai.APITimeoutError as e:
                if attempt == RetryConfig.OPENAI_MAX_RETRIES - 1:
                    logger.error(f"[API] OpenAI timeout - final attempt failed: {str(e)}")
                    raise APIError(f"OpenAI timeout: {str(e)}", "timeout")
                
                logger.warning(f"[API] Timeout, retrying {attempt + 1}/{RetryConfig.OPENAI_MAX_RETRIES}: {str(e)}")
                time.sleep(RetryConfig.OPENAI_RETRY_DELAYS[attempt])
            
            except Exception as e:
                logger.error(f"[API] Unexpected error in OpenAI call: {str(e)}")
                raise APIError(f"Unexpected OpenAI error: {str(e)}", "unknown")
        
        return None  # 실제로는 도달하지 않음
    
    return wrapper


class HTTPRetrySession:
    """HTTP 요청용 재시도 세션"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # 재시도 전략 설정
        retry_strategy = Retry(
            total=RetryConfig.HTTP_MAX_RETRIES,
            backoff_factor=RetryConfig.HTTP_BACKOFF_FACTOR,
            status_forcelist=RetryConfig.HTTP_STATUS_FORCELIST,
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 타임아웃 설정
        self.session.timeout = (10, 30)  # (connect, read)
    
    def get(self, *args, **kwargs):
        """GET 요청"""
        return self.session.get(*args, **kwargs)
    
    def post(self, *args, **kwargs):
        """POST 요청"""
        return self.session.post(*args, **kwargs)


def safe_http_request(url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
    """안전한 HTTP 요청"""
    logger = get_logger()
    
    try:
        session = HTTPRetrySession()
        
        if method.upper() == "GET":
            response = session.get(url, **kwargs)
        elif method.upper() == "POST":
            response = session.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        logger.debug(f"[HTTP] Successful {method} request to {url}")
        return response
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"[HTTP] Connection error for {url}: {str(e)}")
        raise NetworkError(f"Connection failed: {str(e)}")
    
    except requests.exceptions.Timeout as e:
        logger.error(f"[HTTP] Timeout for {url}: {str(e)}")
        raise NetworkError(f"Request timeout: {str(e)}")
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"[HTTP] HTTP error for {url}: {e.response.status_code}: {str(e)}")
        raise NetworkError(f"HTTP {e.response.status_code}: {str(e)}")
    
    except Exception as e:
        logger.error(f"[HTTP] Unexpected error for {url}: {str(e)}")
        raise NetworkError(f"Unexpected HTTP error: {str(e)}")


def handle_git_errors(func: Callable) -> Callable:
    """Git 작업 에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger()
        
        for attempt in range(RetryConfig.GIT_MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # 네트워크 관련 Git 에러
                if any(keyword in error_msg for keyword in ['network', 'connection', 'timeout', 'remote']):
                    if attempt == RetryConfig.GIT_MAX_RETRIES - 1:
                        logger.error(f"[GIT] Network error - final attempt failed: {str(e)}")
                        raise GitOperationError(f"Git network error: {str(e)}")
                    
                    logger.warning(f"[GIT] Network error, retrying {attempt + 1}/{RetryConfig.GIT_MAX_RETRIES}: {str(e)}")
                    time.sleep(RetryConfig.GIT_RETRY_DELAY)
                    continue
                
                # 인증 관련 에러 (재시도하지 않음)
                elif any(keyword in error_msg for keyword in ['authentication', 'permission', 'access']):
                    logger.error(f"[GIT] Authentication/Permission error: {str(e)}")
                    raise GitOperationError(f"Git authentication error: {str(e)}")
                
                # 기타 에러
                else:
                    logger.error(f"[GIT] Unexpected git error: {str(e)}")
                    raise GitOperationError(f"Git error: {str(e)}")
        
        return None  # 실제로는 도달하지 않음
    
    return wrapper


class ErrorRecovery:
    """에러 복구 시스템"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def recover_from_api_failure(self, error: APIError, fallback_data: Optional[Dict] = None) -> Dict:
        """API 실패 시 복구"""
        self.logger.warning(f"[RECOVERY] Attempting recovery from API failure: {error.error_type}")
        
        if error.error_type == "rate_limit_exceeded":
            # Rate limit 시 대기 후 재시도 권장
            return {
                "action": "wait_and_retry",
                "wait_time": error.retry_after or 60,
                "message": "Rate limit exceeded. Wait before retrying."
            }
        
        elif error.error_type in ["timeout", "connection_error"]:
            # 네트워크 문제 시 재시도 권장
            return {
                "action": "retry",
                "message": "Network issue detected. Retry recommended."
            }
        
        elif fallback_data:
            # 폴백 데이터 사용
            self.logger.info("[RECOVERY] Using fallback data")
            return {
                "action": "use_fallback",
                "data": fallback_data,
                "message": "Using fallback data due to API failure."
            }
        
        else:
            # 복구 불가능한 경우
            return {
                "action": "fail",
                "message": f"Cannot recover from {error.error_type} error."
            }
    
    def recover_from_content_failure(self, title: str) -> Optional[Dict]:
        """콘텐츠 생성 실패 시 복구"""
        self.logger.warning(f"[RECOVERY] Attempting to recover content generation for: {title}")
        
        # 제목 단순화 시도
        simplified_title = self._simplify_title(title)
        
        if simplified_title != title:
            return {
                "action": "retry_with_simplified_title",
                "new_title": simplified_title,
                "message": "Retrying with simplified title."
            }
        
        return None
    
    def _simplify_title(self, title: str) -> str:
        """제목 단순화"""
        # 특수 문자 제거
        import re
        simplified = re.sub(r'[^\w\s-]', '', title)
        
        # 길이 제한
        if len(simplified) > 50:
            simplified = simplified[:50].rsplit(' ', 1)[0]
        
        return simplified.strip()
    
    def check_system_health(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        health_check = {
            "timestamp": time.time(),
            "checks": {}
        }
        
        # 디스크 공간 확인
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            health_check["checks"]["disk"] = {
                "status": "ok" if free > 1024**3 else "warning",  # 1GB 여유
                "free_gb": free // (1024**3),
                "message": f"{free // (1024**3)} GB free"
            }
        except Exception as e:
            health_check["checks"]["disk"] = {
                "status": "error",
                "message": f"Cannot check disk usage: {str(e)}"
            }
        
        # 네트워크 연결 확인 (간단한 방법으로 변경)
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            health_check["checks"]["network"] = {
                "status": "ok",
                "message": "Network connectivity OK"
            }
        except Exception as e:
            health_check["checks"]["network"] = {
                "status": "error", 
                "message": f"Network check failed: {str(e)}"
            }
        
        # 로그 디렉터리 확인
        try:
            from pathlib import Path
            log_dir = Path("logs")
            health_check["checks"]["logs"] = {
                "status": "ok" if log_dir.exists() else "error",
                "message": "Log directory accessible" if log_dir.exists() else "Log directory missing"
            }
        except Exception as e:
            health_check["checks"]["logs"] = {
                "status": "error",
                "message": f"Cannot check logs: {str(e)}"
            }
        
        return health_check


def graceful_shutdown(func: Callable) -> Callable:
    """우아한 종료 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger()
        
        try:
            return func(*args, **kwargs)
        
        except KeyboardInterrupt:
            logger.info("[SHUTDOWN] Graceful shutdown initiated by user")
            raise
        
        except SystemExit as e:
            logger.info(f"[SHUTDOWN] System exit with code {e.code}")
            raise
        
        except Exception as e:
            logger.error("[SHUTDOWN] Unexpected error during execution", exception=e)
            
            # 에러 상황에서의 정리 작업
            try:
                # 임시 파일 정리 등
                import tempfile
                import glob
                
                temp_files = glob.glob(tempfile.gettempdir() + "/autoblog_*")
                for temp_file in temp_files:
                    try:
                        Path(temp_file).unlink()
                    except:
                        pass
                        
            except Exception as cleanup_error:
                logger.warning("[SHUTDOWN] Error during cleanup", exception=cleanup_error)
            
            raise
    
    return wrapper


def test_error_handling():
    """에러 핸들링 테스트"""
    logger = get_logger()
    
    logger.info("[TEST] Testing error handling system...")
    
    # HTTP 재시도 테스트 (간단한 테스트로 변경)
    try:
        import requests
        response = requests.get("https://httpbin.org/status/500", timeout=5)
        logger.info("[TEST] HTTP test - unexpected success")
    except Exception as e:
        logger.info(f"[TEST] HTTP test - correctly caught error: {str(e)}")
    
    # 복구 시스템 테스트
    recovery = ErrorRecovery()
    
    # API 실패 복구 테스트
    api_error = APIError("Rate limit exceeded", "rate_limit_exceeded", retry_after=30)
    recovery_plan = recovery.recover_from_api_failure(api_error)
    logger.info(f"[TEST] API recovery plan: {recovery_plan}")
    
    # 시스템 상태 확인 테스트
    health = recovery.check_system_health()
    logger.info(f"[TEST] System health check completed: {len(health['checks'])} checks")
    
    # 재시도 데코레이터 테스트
    @retry_on_failure(max_retries=2, delay=0.1, exceptions=(ValueError,))
    def test_retry():
        import random
        if random.random() < 0.7:  # 70% 실패율
            raise ValueError("Test failure")
        return "success"
    
    try:
        result = test_retry()
        logger.info(f"[TEST] Retry decorator test result: {result}")
    except ValueError as e:
        logger.info(f"[TEST] Retry decorator test - final failure as expected: {str(e)}")
    
    logger.info("[TEST] Error handling tests completed!")
    return True


if __name__ == "__main__":
    test_error_handling()