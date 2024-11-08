from fastapi import HTTPException, Depends
from redis import Redis

from app.core.config import jwt_setting
from app.core.errors.http_exceptions import ForbiddenException
from app.infrastructure.auth.redis_client import get_redis_client

class RedisService:
    def __init__(self, redis_client: Redis):
        self._redis = redis_client

    def save_refresh_token(self, user_id: int, refresh_token: str) -> str:
        self._redis.setex(
            f"refresh_token:{refresh_token}",
            jwt_setting.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            str(user_id)
        )
        return refresh_token

    def validate_refresh_token(self, refresh_token: str) -> int:
        user_id_str: str = self._redis.get(f"refresh_token:{refresh_token}")
        if not user_id_str:
            raise ForbiddenException("Invalid refresh token")
        return int(user_id_str)

    def revoke_refresh_token(self, refresh_token: str) -> None:
        self._redis.delete(f"refresh_token:{refresh_token}")


def get_redis_service(
        redis_client: Redis = Depends(get_redis_client)
) -> RedisService:
    return RedisService(redis_client=redis_client)