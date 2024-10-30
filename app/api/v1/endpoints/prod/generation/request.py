from fastapi import APIRouter, Depends

from app.application.services.generation.dto.query import GetGenerationRequestDetailsResponse
from app.application.services.generation.dto.request import CreateGenerationRequestRequest, \
    CreateGenerationRequestResponse, StartGenerationResponse
from app.application.services.generation.query import GenerationRequestQueryService, \
    get_generation_request_query_service
from app.application.services.generation.request import RequestGenerationApplicationService, \
    get_request_generation_application_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# api/v1/prod/generation/

@router.post("")
def create_generation_request(
        request: CreateGenerationRequestRequest,
        user_id: int = Depends(validate_user_token),
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
) -> CreateGenerationRequestResponse:
    return service.create_generation_request(request, user_id)

@router.post("/{generation_request_id}/start")
async def start_generation(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
) -> StartGenerationResponse:
    return await service.start_generation(generation_request_id, user_id)

@router.get("/{generation_request_id}/details")
def get_generation_request_details(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: GenerationRequestQueryService = Depends(get_generation_request_query_service)
) -> GetGenerationRequestDetailsResponse:
    return service.get_generated_request_details(generation_request_id, user_id)