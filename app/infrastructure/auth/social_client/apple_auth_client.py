from urllib.parse import urlencode

import jwt
from datetime import datetime, timedelta

import requests
from jwt import InvalidTokenError

from app.core.config import oauth_settings
from app.core.errors.http_exceptions import SocialAuthException
from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo
from app.infrastructure.auth.social_client.social_auth_client import SocialAuthClient


class AppleAuthClient(SocialAuthClient):
    @staticmethod
    def get_authorization_url() -> str:
        base_url = "https://appleid.apple.com/auth/authorize"

        params = {
            "client_id": oauth_settings.APPLE_CLIENT_ID,
            "redirect_uri": oauth_settings.APPLE_REDIRECT_URI,
            "response_type": "code id_token",
            "scope": "email",
            "response_mode": "form_post",
            "state": "state"
        }

        return f"{base_url}?{urlencode(params)}"

    @staticmethod
    def _generate_client_secret() -> str:
        """Apple client secret 동적 생성"""
        private_key = oauth_settings.APPLE_PRIVATE_KEY  # .p8 파일 내용
        team_id = oauth_settings.APPLE_TEAM_ID
        client_id = oauth_settings.APPLE_CLIENT_ID
        key_id = oauth_settings.APPLE_KEY_ID

        now = datetime.utcnow()
        exp_time = now + timedelta(minutes=5)  # 5분간 유효

        headers = {
            'kid': key_id
        }

        payload = {
            'iss': team_id,
            'iat': now,
            'exp': exp_time,
            'aud': 'https://appleid.apple.com',
            'sub': client_id,
        }

        client_secret = jwt.encode(
            payload,
            private_key,
            algorithm='ES256',
            headers=headers
        )

        return client_secret

    @staticmethod
    def verify_mobile_token(id_token: str) -> AuthInfo:
        try:
            jwks_url = 'https://appleid.apple.com/auth/keys'
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)

            decoded_info = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=['RS256'],
                audience=oauth_settings.APPLE_CLIENT_ID,
                issuer='https://appleid.apple.com'
            )

            # Apple은 email을 첫 로그인에만 제공할 수 있음
            email = decoded_info.get("email", "")

            return AuthInfo(
                provider="apple",
                social_id=decoded_info["sub"],  # Apple의 unique user ID
                email=email
            )
        except InvalidTokenError:
            raise SocialAuthException("애플 소셜 로그인 중 에러 발생")

    @staticmethod
    def verify_web_token(code: str) -> AuthInfo:
        id_token: str = AppleAuthClient._get_web_id_token(code)
        # 웹 토큰은 signature 검증 생략
        decoded_info = jwt.decode(id_token, options={"verify_signature": False})

        # Apple은 email을 첫 로그인에만 제공할 수 있음
        email = decoded_info.get("email", "")

        return AuthInfo(
            provider="apple",
            social_id=decoded_info["sub"],
            email=email
        )

    @staticmethod
    def _get_web_id_token(code: str) -> str: # 여기가 input이 변경되어야함.
        client_secret = AppleAuthClient._generate_client_secret()

        response = requests.post(
            "https://appleid.apple.com/auth/token",
            data={
                "code": code,
                "client_id": oauth_settings.APPLE_CLIENT_ID,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": oauth_settings.APPLE_REDIRECT_URI
            }
        )
        return response.json()["id_token"]

def get_apple_auth_client():
    return AppleAuthClient()