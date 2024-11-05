import requests
import jwt
import logging
from urllib.parse import urlencode
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.core.errors.http_exceptions import SocialAuthException
from app.core.config import oauth_setting
from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo
from app.infrastructure.auth.social_client.social_auth_client import SocialAuthClient

class GoogleAuthClient(SocialAuthClient):

    @staticmethod
    def get_authorization_url() -> str:
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"

        params = {
            "client_id": oauth_setting.GOOGLE_WEB_CLIENT_ID,
            "redirect_uri": oauth_setting.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email",
            "access_type": "offline",
            "prompt": "select_account"
        }

        return f"{base_url}?{urlencode(params)}"

    @staticmethod
    def verify_mobile_token(id_token: str) -> AuthInfo:
        try:
            logging.info(f"Attempting to verify token: {id_token[:20]}...")  # 토큰 앞부분만 로깅
            logging.info(f"Using client ID: {oauth_setting.GOOGLE_APP_CLIENT_ID}")

            request = google_requests.Request()

            try:
                decoded_info: Dict[str, Any] = google_id_token.verify_oauth2_token(
                    id_token,
                    request,
                    oauth_setting.GOOGLE_APP_CLIENT_ID
                )

                logging.info(f"Successfully decoded token info: {decoded_info}")

                return AuthInfo(
                    provider="google",
                    social_id=decoded_info["sub"],
                    email=decoded_info["email"]
                )

            except ValueError as token_error:
                logging.error(f"Token verification failed. Error: {str(token_error)}")
                logging.error(f"Error type: {type(token_error)}")

                # 토큰 디코딩 시도 (검증 없이)
                try:
                    import jwt
                    unverified_decoded = jwt.decode(id_token, options={"verify_signature": False})
                    logging.info(f"Unverified token contents: {unverified_decoded}")
                except Exception as jwt_error:
                    logging.error(f"Failed to decode token without verification: {str(jwt_error)}")

                raise

        except Exception as e:
            logging.error(f"Unexpected error during verification: {str(e)}", exc_info=True)
            raise SocialAuthException(f"구글 소셜 로그인 중 에러 발생: {str(e)}")

    @staticmethod
    def verify_web_token(code: str) -> AuthInfo:
        id_token: str = GoogleAuthClient._get_web_id_token(code=code)
        # 웹 토큰은 signature 검증 생략
        decoded_info = jwt.decode(id_token, options={"verify_signature": False})
        return AuthInfo(
            provider="google",
            social_id=decoded_info["sub"],
            email=decoded_info["email"]
        )

    @staticmethod
    def _get_web_id_token(code: str) -> str:
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": oauth_setting.GOOGLE_WEB_CLIENT_ID,
                "client_secret": oauth_setting.GOOGLE_CLIENT_SECRET,
                "redirect_uri": oauth_setting.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        return response.json()["id_token"]


def get_google_auth_client() -> GoogleAuthClient:
    return GoogleAuthClient()