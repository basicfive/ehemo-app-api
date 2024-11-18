import logging
from datetime import datetime, UTC, timedelta
from uuid import uuid4
import jwt

from app.core.config import jwt_setting
from app.core.errors.http_exceptions import UnauthorizedException

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
            logger.info("Validating access token.")
            # Decode JWT
            payload: dict = jwt.decode(
                token,
                jwt_setting.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            logger.info("Token successfully decoded. Payload: %s", payload)

            # Return the user ID from the token
            user_id = int(payload["sub"])
            logger.info("Extracted user ID: %d", user_id)
            return user_id

        except jwt.ExpiredSignatureError:
            logger.error("The token has expired.")
            raise UnauthorizedException("Token has expired.")

        except jwt.DecodeError:
            logger.error("Failed to decode token. Token might be invalid: %s", token)
            raise UnauthorizedException("Invalid token.")

        except KeyError:
            logger.error("Token payload does not contain 'sub'. Payload: %s", payload)
            raise UnauthorizedException("Malformed token payload.")

        except jwt.InvalidTokenError as e:
            logger.error("Invalid token error: %s", str(e))
            raise UnauthorizedException("Invalid token.")

def get_auth_token_service() -> AuthTokenService:
    return AuthTokenService()