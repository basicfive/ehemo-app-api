from fastapi.params import Depends
from typing import List, Optional

from app.domain.hair_model.models.hair import HairVariantModel
from app.application.services.generation.dto.query import GenerationRequestStatusResponse
from app.application.services.generation.dto.request import GenerationRequestDetails
from app.core.enums.generation_status import GenerationResultEnum
from app.core.errors.http_exceptions import UnauthorizedException
from app.domain.generation.models.generation import GenerationRequest, ImageGenerationJob
from app.domain.generation.services.generation_domain_service import calculate_remaining_generation_sec
from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.length import LengthInDB
from app.domain.hair_model.schemas.hair.color import ColorInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository, \
    get_generation_request_repository, ImageGenerationJobRepository, get_image_generation_job_repository, \
    GeneratedImageGroupRepository, get_generated_image_group_repository


class GenerationRequestQueryService:
    def __init__(
            self,
            generation_request_repo: GenerationRequestRepository,
            generated_image_group_repo: GeneratedImageGroupRepository,
            image_generation_job_repo: ImageGenerationJobRepository,
    ):
        self.generation_request_repo = generation_request_repo
        self.generated_image_group_repo = generated_image_group_repo
        self.image_generation_job_repo = image_generation_job_repo

    def get_generation_request_status(self, generation_request_id: int, user_id: int):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise UnauthorizedException()

        remaining_sec: int = 0
        generated_image_group_id: Optional[int] = None

        if generation_request.generation_result == GenerationResultEnum.PENDING:
            image_generation_job_list: List[ImageGenerationJob] = (
                self.image_generation_job_repo.get_all_by_generation_request(generation_request_id)
            )
            remaining_sec = calculate_remaining_generation_sec(image_generation_job_list)
        elif generation_request.generation_result == GenerationResultEnum.SUCCEED:
            generated_image_group = self.generated_image_group_repo.get_by_generation_request(generation_request_id)
            generated_image_group_id = generated_image_group.id

        return GenerationRequestStatusResponse(
            generation_status=generation_request.generation_result,
            remaining_sec=remaining_sec,
            generated_image_group_id=generated_image_group_id
        )

    def get_generated_request_details(self, generation_request_id: int, user_id: int):
        generation_request_with_relation: GenerationRequest = (
            self.generation_request_repo.get_with_all_relations(generation_request_id)
        )

        if generation_request_with_relation.user_id != user_id:
            raise UnauthorizedException()

        hair_variant_model_with_relation: HairVariantModel = generation_request_with_relation.hair_variant_model
        return GenerationRequestDetails(
            generation_request_id=generation_request_with_relation.id,
            gender=GenderInDB.model_validate(hair_variant_model_with_relation.gender),
            hair_style=HairStyleInDB.model_validate(hair_variant_model_with_relation.hair_style),
            length=LengthInDB.model_validate(hair_variant_model_with_relation.length),
            color=ColorInDB.model_validate(hair_variant_model_with_relation.color),
            background=BackgroundInDB.model_validate(generation_request_with_relation.background),
            image_resolution=ImageResolutionInDB.model_validate(generation_request_with_relation.image_resolution)
        )

def get_generation_request_query_service(
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        generated_image_group_repo: GeneratedImageGroupRepository = Depends(get_generated_image_group_repository),
        image_generation_job_repo: ImageGenerationJobRepository = Depends(get_image_generation_job_repository),
) -> GenerationRequestQueryService:
    return GenerationRequestQueryService(
        generation_request_repo=generation_request_repo,
        generated_image_group_repo=generated_image_group_repo,
        image_generation_job_repo=image_generation_job_repo,
    )
