from fastapi import Depends
from sqlalchemy.exc import NoResultFound

from app.application.services.user.dto.auth import UserInfo, TokenResponse
from app.domain.user.schemas.user import UserCreate
from app.domain.user.services.auth import AuthTokenService, get_auth_token_service
from app.infrastructure.auth.social_client.apple_auth_client import get_apple_auth_client
from app.infrastructure.auth.social_client.dto.auth_data import AuthInfo
from app.infrastructure.auth.social_client.google_auth_client import get_google_auth_client
from app.infrastructure.auth.redis_service import RedisService, get_redis_service
from app.infrastructure.auth.social_client.kakao_auth_client import get_kakao_auth_client
from app.infrastructure.auth.social_client.social_auth_client import SocialAuthClient
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository
from app.domain.user.models.user import User

class UserAuthApplicationService:
    def __init__(
            self,
            user_repo: UserRepository,
            redis_service: RedisService,
            auth_token_service: AuthTokenService,
            social_auth_client: SocialAuthClient
    ):
        self.user_repo = user_repo
        self.redis_service = redis_service
        self.auth_token_service = auth_token_service
        self.social_auth_client = social_auth_client

    def mobile_login(self, id_token: str) -> TokenResponse:
        auth_info: AuthInfo = self.social_auth_client.verify_mobile_token(id_token)

        user_info = UserInfo(**auth_info.model_dump())
        user: User = self._get_or_create_user(user_info)

        """
        TODO: 토큰 생성과 refresh 토큰 저장이 구분되어있음.
        도메인이 repo를 갖지 못하도록 해서 발생하는 문제
        애플리케이션에서 refresh token 의 저장까지 고려해야한다.
        """
        access_token, refresh_token = self.auth_token_service.create_tokens(user.id)
        self.redis_service.save_refresh_token(user.id, refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def get_web_login_url(self) -> str:
        return self.social_auth_client.get_authorization_url()

    def web_auth_callback(self, code: str) -> TokenResponse:
        auth_info: AuthInfo = self.social_auth_client.verify_web_token(code)

        user_info = UserInfo(**auth_info.model_dump())
        user: User = self._get_or_create_user(user_info)

        access_token, refresh_token = self.auth_token_service.create_tokens(user.id)
        self.redis_service.save_refresh_token(user.id, refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def logout(self, refresh_token: str) -> bool:
        self.redis_service.revoke_refresh_token(refresh_token)
        return True

    # FIXME: Atomic 하지 않음. 같은 user 의 동시 요청 시, redis 에 같은 user_id 의 여러 refresh token 이 저장됨.
    # 우선 앱 쪽에서 같은 user 의 refresh token 요청은 동기적으로 처리하는 것으로 해결, 추후 하단 코드 개선.
    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        all_refresh_tokens = self.redis_service.get_all_refresh_tokens()

        print(f"\n===== Current Active Sessions =====")
        for token, user_id in all_refresh_tokens:
            print(f"\nUser ID: {user_id}")
            print(f"Refresh Token: {token}")

        user_id = self.redis_service.validate_refresh_token(refresh_token)

        access_token, new_refresh_token = self.auth_token_service.create_tokens(user_id)

        print(f"access token: {access_token}")

        print(f"\n================================")

        self.redis_service.save_refresh_token(user_id, new_refresh_token)
        self.redis_service.revoke_refresh_token(refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    def _get_or_create_user(self, user_info: UserInfo) -> User:
        try:
            # TODO: DB에서 리소스가 없는 경우 에러 반환하지 않는 쪽으로 가야하는가?
            db_user: User = self.user_repo.get_by_social_account(provider=user_info.provider, social_id=user_info.social_id)
            return db_user
        except NoResultFound:
            db_user = self.user_repo.create(obj_in=UserCreate(**user_info.model_dump()))
            return db_user


def get_google_user_auth_application_service(
        user_repo: UserRepository = Depends(get_user_repository),
        redis_service: RedisService = Depends(get_redis_service),
        auth_token_service: AuthTokenService = Depends(get_auth_token_service),
        social_auth_client: SocialAuthClient = Depends(get_google_auth_client)
) -> UserAuthApplicationService:
    return UserAuthApplicationService(
        user_repo=user_repo,
        redis_service=redis_service,
        auth_token_service=auth_token_service,
        social_auth_client=social_auth_client
    )

def get_kakao_user_auth_application_service(
        user_repo: UserRepository = Depends(get_user_repository),
        redis_service: RedisService = Depends(get_redis_service),
        auth_token_service: AuthTokenService = Depends(get_auth_token_service),
        social_auth_client: SocialAuthClient = Depends(get_kakao_auth_client)
) -> UserAuthApplicationService:
    return UserAuthApplicationService(
        user_repo=user_repo,
        redis_service=redis_service,
        auth_token_service=auth_token_service,
        social_auth_client=social_auth_client
    )

def get_apple_user_auth_application_service(
        user_repo: UserRepository = Depends(get_user_repository),
        redis_service: RedisService = Depends(get_redis_service),
        auth_token_service: AuthTokenService = Depends(get_auth_token_service),
        social_auth_client: SocialAuthClient = Depends(get_apple_auth_client)
) -> UserAuthApplicationService:
    return UserAuthApplicationService(
        user_repo=user_repo,
        redis_service=redis_service,
        auth_token_service=auth_token_service,
        social_auth_client=social_auth_client
    )


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

def validate_user_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        auth_token_service: AuthTokenService = Depends(get_auth_token_service)
):
    token = credentials.credentials
    return auth_token_service.validate_access_token(token)
