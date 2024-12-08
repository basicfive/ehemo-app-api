from typing import Optional

from fastapi import HTTPException

from app.core.errors.error_messages import USER_HAS_NOT_ENOUGH_TOKEN_MESSAGE, CONCURRENT_GENERATION_REQUEST_MESSAGE


class CustomHttpException(HTTPException):
    def __init__(
            self,
            status_code: int,
            error_code: str,
            message: str,
            context: Optional[str],
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "context": context
            }
        )

# HTTP EXCEPTIONS
class NotFoundException(CustomHttpException):
    def __init__(self, message: str, context: Optional[str]):
        super().__init__(404, "Not Found", message, context)

class UnauthorizedException(CustomHttpException):
    def __init__(self, message: str, context: Optional[str]):
        super().__init__(401, "Unauthorized", message, context)

class ForbiddenException(CustomHttpException):
    def __init__(self, message: str, context: Optional[str]):
            super().__init__(403, "Forbidden", message, context)

class ValueException(CustomHttpException):
    def __init__(self, message: str, context: Optional[str]):
        super().__init__(400, "Bad Request", message, context)

class ResourceConflictException(CustomHttpException):
    def __init__(self, message: str, context: Optional[str]):
        super().__init__(409, "Conflict", message, context)


# SPECIFIC EXCEPTIONS - message 가 client에 그대로 표기됨.
class ResourceNotFoundException(NotFoundException):
    def __init__(self, context: str = None):
        super().__init__("Requested resource is not found", context)

class AccessUnauthorizedException(UnauthorizedException):
    def __init__(self, context: str = None):
        super().__init__("Access Unauthorized", context)

class SocialAuthException(UnauthorizedException):
    def __init__(self, context: str = None):
        super().__init__("Oauth error", context)

class ForbiddenRequestException(ForbiddenException):
    def __init__(self, context: str = None):
        super().__init__("Forbidden request", context)

class RequestValueException(ValueException):
    def __init__(self, context: str = None):
        super().__init__("Request value is incorrect", context)

class ConcurrentGenerationRequestError(ResourceConflictException):
    def __init__(self, context: str = None):
        super().__init__(CONCURRENT_GENERATION_REQUEST_MESSAGE, context)


# 내가 정의한 에러 코드로 에러 발행
class UserHasNotEnoughTokenException(CustomHttpException):
    def __init__(self, context: str = None):
        super().__init__(440, "UserToken", USER_HAS_NOT_ENOUGH_TOKEN_MESSAGE, context)
