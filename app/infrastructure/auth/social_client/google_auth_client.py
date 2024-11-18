import logging
import requests
from urllib.parse import urlencode
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.errors.http_exceptions import SocialAuthException
from app.core.config import oauth_setting
from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo
from app.infrastructure.auth.social_client.social_auth_client import SocialAuthClient

class GoogleAuthClient(SocialAuthClient):
    @staticmethod
    def get_authorization_url() -> str:
        """웹 로그인용 Google OAuth 2.0 인증 URL 생성"""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": oauth_setting.GOOGLE_CLIENT_ID,
            "redirect_uri": oauth_setting.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email",
            "access_type": "offline",
            "prompt": "consent"
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
        """Google OAuth 2.0 인증 코드 검증 및 사용자 정보 획득"""
        try:
            # 토큰 교환 요청
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": oauth_setting.GOOGLE_CLIENT_ID,
                    "client_secret": oauth_setting.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": oauth_setting.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )

            token_response.raise_for_status()
            token_data = token_response.json()
            id_token_str = token_data.get("id_token")

            if not id_token_str:
                logging.error("id_token missing from response")
                raise ValueError("Failed to obtain id_token")

            request_adapter = google_requests.Request()
            decoded_token = id_token.verify_oauth2_token(
                id_token_str,
                request_adapter,
                oauth_setting.GOOGLE_CLIENT_ID
            )

            return AuthInfo(
                provider="google",
                social_id=decoded_token["sub"],
                email=decoded_token["email"]
            )

        except ValueError as ve:
            logging.error(f"Invalid token: {str(ve)}")
            raise SocialAuthException("구글 웹 로그인 중 유효하지 않은 토큰 발생")
        except requests.exceptions.RequestException as re:
            logging.error(f"Request failed: {str(re)}")
            raise SocialAuthException("구글 API 요청 중 에러 발생")
        except Exception as e:
            logging.error(f"Web token verification failed: {str(e)}")
            raise SocialAuthException("구글 웹 로그인 중 에러 발생")

def get_google_auth_client() -> GoogleAuthClient:
    return GoogleAuthClient()