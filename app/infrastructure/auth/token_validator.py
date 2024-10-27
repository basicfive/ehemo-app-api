from jwt import decode, InvalidTokenError
from fastapi import HTTPException

from app.core.config import settings

# TODO: 구글 oauth 버전 기준으로 작성됨. 나머지 플랫폼 호환성 고려
def validate_token(token: str) -> str:
    try:
        payload = decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")



