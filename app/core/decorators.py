from functools import wraps
from typing import Callable, TypeVar, cast, List, Generic
import logging
import functools
from typing import Callable, Optional

from app.core.errors.exceptions import ResourceNotFoundException, ParentKeyNotFoundException

T = TypeVar('T')

def handle_not_found(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ValueError:
            raise ResourceNotFoundException()
    return cast(Callable[..., T], wrapper)

def handle_parent_not_found(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ValueError:
            raise ParentKeyNotFoundException()
    return cast(Callable[..., T], wrapper)

def log_errors(error_message: Optional[str] = None, logger=None):
    """
    커스텀 에러 메시지를 지정할 수 있는 에러 로깅 데코레이터

    Args:
        error_message: 에러 발생시 출력할 커스텀 메시지 (기본값: None)
        logger: 커스텀 로거 (기본값: None, root 로거 사용)
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            used_logger = logger or logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 커스텀 메시지가 있으면 해당 메시지 사용, 없으면 기본 메시지
                message = error_message or f"{func.__name__} failed"
                used_logger.error(f"{message}: {str(e)}")
                raise

        return wrapper

    return decorator