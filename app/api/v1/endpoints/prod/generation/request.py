from fastapi import APIRouter, Depends

from app.application.services.generation.dto.generation_request import CreateGenerationRequestRequest, \
    CreateGenerationRequestResponse, StartGenerationResponse
from app.application.services.generation.request_generation import RequestGenerationApplicationService, \
    get_request_generation_application_service
from app.application.services.user.user_auth import validate_user_token

router = APIRouter()

# api/v1/prod/generation/

@router.post("/request")
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