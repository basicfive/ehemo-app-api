from fastapi.params import Depends
from typing import List
from datetime import datetime, UTC

from app.application.query.dto.hair_model_details import HairModelDetails
from app.application.query.hair_model_query import HairModelQueryService, get_hair_model_query_service
from app.application.services.generation.dto.query import GenerationRequestStatusResponse
from app.application.services.generation.dto.request import GenerationRequestDetails
from app.core.enums.generation_status import GenerationResultEnum
from app.core.errors.http_exceptions import UnauthorizedException, ResourceNotFoundException
from app.domain.generation.models.generation import GenerationRequest, ImageGenerationJob
from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.length import LengthInDB
from app.domain.hair_model.schemas.hair.color import ColorInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository, \
    get_generation_request_repository, ImageGenerationJobRepository, get_image_generation_job_repository


class GenerationRequestQueryService:
    def __init__(
            self,
            generation_request_repo: GenerationRequestRepository,
            image_generation_job_repo: ImageGenerationJobRepository,
            hair_model_query_service: HairModelQueryService
    ):
        self.generation_request_repo = generation_request_repo
        self.image_generation_job_repo = image_generation_job_repo
        self.hair_model_query_service = hair_model_query_service

    def get_generation_request_status(self, generation_request_id: int, user_id: int):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise UnauthorizedException()

        remaining_sec: int = 0
        if generation_request.generation_result != GenerationResultEnum.PENDING:
            remaining_sec = self._calculate_remaining_generation_sec(generation_request_id)

        return GenerationRequestStatusResponse(
            generation_status=generation_request.generation_result,
            remaining_sec=remaining_sec
        )

    def _calculate_remaining_generation_sec(self, generation_request_id: int) -> int:
        image_generation_job_list: List[ImageGenerationJob] = (
            self.image_generation_job_repo.get_all_by_generation_request(generation_request_id=generation_request_id)
        )
        if not image_generation_job_list:
            raise ResourceNotFoundException()

        # 가장 늦은 expires_at 찾기
        latest_expire = max(job.expires_at for job in image_generation_job_list)

        # 현재 UTC 시간과의 차이 계산
        time_difference = latest_expire - datetime.now(UTC)

        # 음수가 되면(만료시간이 지났으면) 0 반환, 아니면 초 단위로 변환하여 반환
        return max(0, int(time_difference.total_seconds()))

    def get_generated_request_details(self, generation_request_id: int, user_id: int):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise UnauthorizedException()

        hair_model_details: HairModelDetails = self.hair_model_query_service.get_hair_model_details(
            hair_variant_model_id=generation_request.hair_variant_model_id,
            background_id=generation_request.background_id,
            image_resolution_id=generation_request.image_resolution_id
        )
        return GenerationRequestDetails(
            generation_request_id=generation_request.id,
            gender=GenderInDB.model_validate(hair_model_details.gender),
            hair_style=HairStyleInDB.model_validate(hair_model_details.hair_style),
            length=LengthInDB.model_validate(hair_model_details.length),
            color=ColorInDB.model_validate(hair_model_details.color),
            background=BackgroundInDB.model_validate(hair_model_details.background),
            image_resolution=ImageResolutionInDB.model_validate(hair_model_details.image_resolution)
        )

def get_generation_request_query_service(
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        image_generation_job_repo: ImageGenerationJobRepository = Depends(get_image_generation_job_repository),
        hair_model_query_service: HairModelQueryService = Depends(get_hair_model_query_service)
) -> GenerationRequestQueryService:
    return GenerationRequestQueryService(
        generation_request_repo=generation_request_repo,
        image_generation_job_repo=image_generation_job_repo,
        hair_model_query_service=hair_model_query_service
    )
