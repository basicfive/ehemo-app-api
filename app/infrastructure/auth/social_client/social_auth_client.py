from abc import ABC, abstractmethod

from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo


class SocialAuthClient(ABC):

    @staticmethod
    @abstractmethod
    def get_authorization_url() -> str:
        pass

    @staticmethod
    @abstractmethod
    def verify_mobile_token(id_token: str) -> AuthInfo:
        pass

    @staticmethod
    @abstractmethod
    def verify_web_token(code: str) -> AuthInfo:
        pass