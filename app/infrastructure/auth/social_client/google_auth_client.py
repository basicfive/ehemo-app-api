import logging
import requests
from urllib.parse import urlencode

from app.core.errors.http_exceptions import SocialAuthException
from app.core.config import oauth_setting
from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo
from app.infrastructure.auth.social_client.social_auth_client import SocialAuthClient

class GoogleAuthClient(SocialAuthClient):
    @staticmethod
    def get_authorization_url() -> str:
        """웹 로그인용 Firebase 인증 URL 생성"""
        base_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp"
        params = {
            "key": oauth_setting.FIREBASE_API_KEY,
            "providerId": "google.com",
            "continueUri": oauth_setting.GOOGLE_REDIRECT_URI
        }
        return f"{base_url}?{urlencode(params)}"

    @staticmethod
    def verify_mobile_token(id_token: str) -> AuthInfo:
        """Firebase 모바일 ID 토큰 검증"""
        try:
            logging.info(f"Attempting to verify Firebase mobile token: {id_token[:20]}...")

            response = requests.post(
                "https://identitytoolkit.googleapis.com/v1/accounts:lookup",
                params={"key": oauth_setting.FIREBASE_API_KEY},
                json={"idToken": id_token}
            )

            if "error" in response.json():
                raise ValueError(response.json()["error"]["message"])

            user_data = response.json()["users"][0]

            return AuthInfo(
                provider="google",
                social_id=user_data["localId"],
                email=user_data["email"]
            )

        except Exception as e:
            logging.error(f"Mobile token verification failed: {str(e)}")
            raise SocialAuthException("구글 앱 로그인 중 에러 발생")

    @staticmethod
    def verify_web_token(code: str) -> AuthInfo:
        """Firebase 웹 인증 코드 검증"""
        try:
            logging.info("Attempting to verify Firebase web token...")

            response = requests.post(
                "https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp",
                params={"key": oauth_setting.FIREBASE_API_KEY},
                json={
                    "postBody": f"code={code}&providerId=google.com",
                    "requestUri": oauth_setting.GOOGLE_REDIRECT_URI,
                    "returnIdpCredential": True,
                    "returnSecureToken": True
                }
            )

            if "error" in response.json():
                raise ValueError(response.json()["error"]["message"])

            data = response.json()

            return AuthInfo(
                provider="google",
                social_id=data["localId"],
                email=data["email"]
            )

        except Exception as e:
            logging.error(f"Web token verification failed: {str(e)}")
            raise SocialAuthException("구글 웹 로그인 중 에러 발생")

def get_google_auth_client() -> GoogleAuthClient:
    return GoogleAuthClient()