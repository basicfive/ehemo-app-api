from datetime import datetime, UTC, timedelta
from uuid import uuid4
import jwt

from app.core.config import jwt_setting
from app.core.errors.http_exceptions import UnauthorizedException


class AuthTokenService:
    @staticmethod
    def create_tokens(
            user_id: int,
            expire_minutes: int = jwt_setting.ACCESS_TOKEN_EXPIRE_MINUTES
    ) -> tuple[str, str]:
        exp = datetime.now(UTC) + timedelta(minutes=expire_minutes)
        access_token = jwt.encode(
            {"sub": user_id, "exp": exp},
            jwt_setting.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        refresh_token = str(uuid4())
        return access_token, refresh_token

    @staticmethod
    def validate_access_token(token: str) -> int:
        try:
            payload: dict = jwt.decode(token, jwt_setting.JWT_SECRET_KEY, algorithms=["HS256"])
            return int(payload["sub"])
        except jwt.InvalidTokenError:
            raise UnauthorizedException()

def get_auth_token_service() -> AuthTokenService:
    return AuthTokenService()