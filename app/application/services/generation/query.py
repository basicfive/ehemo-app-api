from fastapi.params import Depends

from app.application.query.dto.hair_model_details import HairModelDetails
from app.application.query.hair_model_query import HairModelQueryService, get_hair_model_query_service
from app.application.services.generation.dto.query import GetGenerationRequestDetailsResponse
from app.core.errors.http_exceptions import UnauthorizedException
from app.domain.generation.models.generation import GenerationRequest
from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.length import LengthInDB
from app.domain.hair_model.schemas.hair.color import ColorInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository, \
    get_generation_request_repository


class GenerationRequestQueryService:
    def __init__(
            self,
            generation_request_repo: GenerationRequestRepository,
            hair_model_query_service: HairModelQueryService
    ):
        self.generation_request_repo = generation_request_repo
        self.hair_model_query_service = hair_model_query_service


    def get_generated_request_details(self, generation_request_id: int, user_id: int):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise UnauthorizedException()

        hair_model_details: HairModelDetails = self.hair_model_query_service.get_hair_model_details(
            hair_variant_model_id=generation_request.hair_variant_model_id,
            background_id=generation_request.background_id,
            image_resolution_id=generation_request.image_resolution_id
        )
        return GetGenerationRequestDetailsResponse(
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
        hair_model_query_service: HairModelQueryService = Depends(get_hair_model_query_service)
) -> GenerationRequestQueryService:
    return GenerationRequestQueryService(
        generation_request_repo=generation_request_repo,
        hair_model_query_service=hair_model_query_service
    )
