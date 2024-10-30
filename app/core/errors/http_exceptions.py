from fastapi import HTTPException

class CustomHttpException(HTTPException):
    def __init__(
            self,
            status_code: int,
            error_code: str,
            message: str,
            context: str
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "context": context
            }
        )

class ResourceNotFoundException(CustomHttpException):
    def __init__(self, context: str = None):
        super().__init__(404, "Not Found", "Requested resource is not found", context)

class UnauthorizedException(CustomHttpException):
    def __init__(self, context: str = None):
        super().__init__(401, "Unauthorized", "Access Unauthorized", context)

class SocialAuthException(CustomHttpException):
    def __init__(self, context: str = None):
        super().__init__(401, "Unauthorized", "Oauth error", context)

class ForbiddenException(CustomHttpException):
    def __init__(self, context: str = None):
        super().__init__(403, "Forbidden", "Forbidden request", context)

class ValueException(CustomHttpException):
    def __init__(self, context: str = None):
        super().__init__(400, "Bad Request", "Request value is incorrect", context)


