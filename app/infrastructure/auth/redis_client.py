from redis import Redis
from app.core.config import redis_settings
from typing import Optional

_redis_client: Optional[Redis] = None

def get_redis_client() -> Redis:
    """
    Redis 클라이언트의 싱글톤 인스턴스를 반환
    :return:
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            decode_responses=True
        )

    return _redis_client
