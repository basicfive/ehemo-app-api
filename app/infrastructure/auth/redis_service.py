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

    def get_all_refresh_tokens(self) -> list[tuple[str, str]]:
        # refresh_token:* 패턴으로 모든 refresh 토큰 키를 찾습니다
        all_tokens = []
        cursor = 0
        pattern = "refresh_token:*"

        while True:
            cursor, keys = self._redis.scan(cursor, pattern, count=100)
            for key in keys:
                # 키에서 실제 토큰 값 추출 (refresh_token: 제거)
                token = key.decode('utf-8').split(':')[1]
                user_id = self._redis.get(key).decode('utf-8')
                all_tokens.append((token, user_id))

            if cursor == 0:
                break

        return all_tokens


def get_redis_service(
        redis_client: Redis = Depends(get_redis_client)
) -> RedisService:
    return RedisService(redis_client=redis_client)