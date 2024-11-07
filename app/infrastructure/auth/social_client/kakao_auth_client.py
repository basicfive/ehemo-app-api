from urllib.parse import urlencode
import jwt

import requests
from jwt import InvalidTokenError

from app.core.config import oauth_setting
from app.core.errors.http_exceptions import SocialAuthException
from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo
from app.infrastructure.auth.social_client.social_auth_client import SocialAuthClient
import logging

logger = logging.getLogger(__name__)

class KakaoAuthClient(SocialAuthClient):
    @staticmethod
    def get_authorization_url() -> str:
        base_url = "https://kauth.kakao.com/oauth/authorize"

        params = {
            "client_id": oauth_setting.KAKAO_CLIENT_ID,
            "redirect_uri": oauth_setting.KAKAO_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid account_email",
            "prompt": "select_account"
        }

        return f"{base_url}?{urlencode(params)}"

    @staticmethod
    def verify_mobile_token(id_token: str) -> AuthInfo:
        try:
            jwks_url = 'https://kauth.kakao.com/.well-known/jwks.json'
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)

            decoded_info = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=['RS256'],
                audience=oauth_setting.KAKAO_CLIENT_ID,
                issuer='https://kauth.kakao.com'
            )

            return AuthInfo(
                provider="kakao",
                social_id=decoded_info["sub"],
                email=decoded_info["email"]
            )
        except InvalidTokenError as e:
            print(e)
            raise SocialAuthException("카카오 소셜 로그인 중 에러 발생")

    @staticmethod
    def verify_web_token(code: str) -> AuthInfo:
        logger.info(f"code : {code}")
        id_token: str = KakaoAuthClient._get_web_id_token(code)
        # 웹 토큰은 signature 검증 생략
        decoded_info = jwt.decode(id_token, options={"verify_signature": False})
        return AuthInfo(
            provider="kakao",
            social_id=decoded_info["sub"],
            email=decoded_info["email"]
        )

    @staticmethod
    def _get_web_id_token(code: str) -> str:
        response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "code": code,
                "client_id": oauth_setting.KAKAO_CLIENT_ID,
                "client_secret": oauth_setting.KAKAO_CLIENT_SECRET,
                "redirect_uri": oauth_setting.KAKAO_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        logger.info(response.json()["id_token"])
        return response.json()["id_token"]


def get_kakao_auth_client():
    return KakaoAuthClient()