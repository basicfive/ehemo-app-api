from functools import wraps
from typing import Callable, TypeVar, cast, List, Generic

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
