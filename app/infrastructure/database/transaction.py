import asyncio
from typing import TypeVar
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, Callable, Awaitable

T = TypeVar('T')

def transactional(func: Callable[..., Union[T, Awaitable[T]]]) -> Callable[..., Union[T, Awaitable[T]]]:
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        service_instance = args[0]
        uow = service_instance.unit_of_work
        try:
            result = await func(*args, **kwargs)
            uow.commit()
            return result
        except SQLAlchemyError as e:
            uow.rollback()
            raise
        except Exception as e:
            uow.rollback()
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        service_instance = args[0]
        uow = service_instance.unit_of_work
        try:
            result = func(*args, **kwargs)
            uow.commit()
            return result
        except SQLAlchemyError as e:
            uow.rollback()
            raise
        except Exception as e:
            uow.rollback()
            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper