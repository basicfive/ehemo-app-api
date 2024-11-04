from typing import Dict, Type, Any
from sqlalchemy.orm import Session
from functools import lru_cache

from app.infrastructure.s3.s3_client import S3Client
from app.infrastructure.fcm.fcm_service import FCMService

from app.infrastructure.repositories.hair_model.hair_model import (
    HairVariantModelRepository,
    ColorRepository,
    SpecificColorRepository,
    LengthRepository,
    HairStyleRepository,
    GenderRepository,
    BackgroundRepository,
    ImageResolutionRepository,
    LoRAModelRepository,
    PostureAndClothingRepository
)
from app.application.query.hair_model_query import HairModelQueryService


class DependencyContainer:
    """의존성 관리를 위한 컨테이너 클래스"""

    def __init__(self, db_session: Session):
        self._db = db_session
        self._instances: Dict[Type, Any] = {}

    @property
    def db(self) -> Session:
        return self._db

    @lru_cache()
    def get_repository(self, repo_class: Type) -> Any:
        """Repository 인스턴스를 가져오거나 생성"""
        if repo_class not in self._instances:
            self._instances[repo_class] = repo_class(db=self._db)
        return self._instances[repo_class]

    @property
    def s3_client(self) -> S3Client:
        if S3Client not in self._instances:
            self._instances[S3Client] = S3Client()
        return self._instances[S3Client]

    @property
    def fcm_service(self) -> FCMService:
        if FCMService not in self._instances:
            self._instances[FCMService] = FCMService()
        return self._instances[FCMService]

    @property
    def hair_model_query_service(self) -> HairModelQueryService:
        if HairModelQueryService not in self._instances:
            self._instances[HairModelQueryService] = HairModelQueryService(
                hair_variant_model_repo=self.get_repository(HairVariantModelRepository),
                color_repo=self.get_repository(ColorRepository),
                specific_color_repo=self.get_repository(SpecificColorRepository),
                length_repo=self.get_repository(LengthRepository),
                hair_style_repo=self.get_repository(HairStyleRepository),
                gender_repo=self.get_repository(GenderRepository),
                background_repo=self.get_repository(BackgroundRepository),
                image_resolution_repo=self.get_repository(ImageResolutionRepository),
                lora_model_repo=self.get_repository(LoRAModelRepository),
                posture_and_clothing_repo=self.get_repository(PostureAndClothingRepository)
            )
        return self._instances[HairModelQueryService]

    def cleanup(self):
        """리소스 정리"""
        if self._db:
            self._db.close()
        self._instances.clear()