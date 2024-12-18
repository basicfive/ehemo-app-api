from fastapi import Depends
from redis import Redis

from app.core.config import jwt_settings
from app.core.errors.http_exceptions import ForbiddenRequestException
from app.infrastructure.auth.redis_client import get_redis_client

class RedisService:
    def __init__(self, redis_client: Redis):
        self._redis = redis_client

    def save_refresh_token(self, user_id: int, refresh_token: str) -> str:
        self._redis.setex(
            f"refresh_token:{refresh_token}",
            jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            str(user_id)
        )
        return refresh_token

    def validate_refresh_token(self, refresh_token: str) -> int:
        user_id_str: str = self._redis.get(f"refresh_token:{refresh_token}")
        if not user_id_str:
            raise ForbiddenRequestException("Invalid refresh token")
        return int(user_id_str)

    def revoke_refresh_token(self, refresh_token: str) -> None:
        self._redis.delete(f"refresh_token:{refresh_token}")

    def get_all_refresh_tokens(self) -> list[tuple[str, str]]:
        all_tokens = []
        cursor = 0
        pattern = "refresh_token:*"

        while True:
            cursor, keys = self._redis.scan(cursor, pattern, count=100)
            for key in keys:
                # key가 이미 문자열인 경우와 bytes인 경우를 모두 처리
                token_key = key.decode('utf-8') if isinstance(key, bytes) else key
                token = token_key.split(':')[1]

                # value도 마찬가지로 bytes와 문자열 케이스 모두 처리
                value = self._redis.get(key)
                user_id = value.decode('utf-8') if isinstance(value, bytes) else value

                all_tokens.append((token, user_id))

            if cursor == 0:
                break

        return all_tokens

def get_redis_service(
        redis_client: Redis = Depends(get_redis_client)
) -> RedisService:
    return RedisService(redis_client=redis_client)