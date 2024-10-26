from fastapi import APIRouter, Depends

from app.application.services.generation.dto.generation_request import CreateGenerationRequestRequest, \
    CreateGenerationRequestResponse, StartGenerationResponse
from app.application.services.generation.request_generation import RequestGenerationApplicationService, \
    get_request_generation_application_service

router = APIRouter()

# api/v1/prod/generation/request

@router.post("/request")
def create_generation_request(
        request: CreateGenerationRequestRequest,
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
) -> CreateGenerationRequestResponse:
    return service.create_generation_request(request)

@router.post("/start")
async def start_generation(
        generation_request_id: int,
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
) -> StartGenerationResponse:
    return await service.start_generation(generation_request_id)