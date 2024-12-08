import logging
from datetime import datetime, UTC, timedelta
from uuid import uuid4
import jwt

from app.core.config import jwt_setting
from app.core.errors.http_exceptions import AccessUnauthorizedException

logger = logging.getLogger()

class AuthTokenService:
    @staticmethod
    def create_tokens(
            user_id: int,
            expire_minutes: int = jwt_setting.ACCESS_TOKEN_EXPIRE_MINUTES
    ) -> tuple[str, str]:
        exp = datetime.now(UTC) + timedelta(minutes=expire_minutes)
        access_token = jwt.encode(
            {"sub": str(user_id), "exp": exp},
            jwt_setting.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        refresh_token = str(uuid4())
        return access_token, refresh_token

    @staticmethod
    def validate_access_token(token: str) -> int:
        try:
            # Decode JWT
            payload: dict = jwt.decode(
                token,
                jwt_setting.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )

            # Return the user ID from the token
            user_id = int(payload["sub"])
            return user_id

        except jwt.ExpiredSignatureError:
            logger.error("The token has expired.")
            raise AccessUnauthorizedException("Token has expired.")

        except jwt.DecodeError:
            logger.error("Failed to decode token. Token might be invalid: %s", token)
            raise AccessUnauthorizedException("Invalid token.")

        except KeyError:
            logger.error("Token payload does not contain 'sub'. Payload: %s", payload)
            raise AccessUnauthorizedException("Malformed token payload.")

        except jwt.InvalidTokenError as e:
            logger.error("Invalid token error: %s", str(e))
            raise AccessUnauthorizedException("Invalid token.")

def get_auth_token_service() -> AuthTokenService:
    return AuthTokenService()