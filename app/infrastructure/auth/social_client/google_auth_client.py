import requests
from urllib.parse import urlencode

from app.core.errors.http_exceptions import SocialAuthException
from app.core.config import base_settings, oauth_setting
from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo
from app.infrastructure.auth.social_client.social_auth_client import SocialAuthClient

class GoogleAuthClient(SocialAuthClient):

    @staticmethod
    def get_authorization_url() -> str:
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"

        params = {
            "client_id": oauth_setting.GOOGLE_CLIENT_ID,
            "redirect_uri": oauth_setting.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email",
            "access_type": "offline",
            "prompt": "select_account"
        }

        return f"{base_url}?{urlencode(params)}"

    @staticmethod
    def verify_mobile_token(id_token: str) -> AuthInfo:
        response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token}
        )

        if response.status_code != 200:
            raise SocialAuthException("Invalid Google token")

        data = response.json()

        if data["aud"] != base_settings.GOOGLE_CLIENT_ID:
            raise SocialAuthException("Invalid client ID")

        return AuthInfo(
            provider="google",
            social_id=data["sub"],
            email=data["email"]
        )

    @staticmethod
    def verify_web_token(code: str) -> AuthInfo:
        access_token: str = GoogleAuthClient._get_web_token(code=code)
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise SocialAuthException("Invalid access token")

        data = response.json()

        return AuthInfo(
            provider="google",
            social_id=data["sub"],
            email=data["email"]
        )

    @staticmethod
    def _get_web_token(code: str) -> str:
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": oauth_setting.GOOGLE_CLIENT_ID,
                "client_secret": oauth_setting.GOOGLE_CLIENT_SECRET,
                "redirect_uri": oauth_setting.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        return response.json()["access_token"]


def get_google_auth_client() -> GoogleAuthClient:
    return GoogleAuthClient()