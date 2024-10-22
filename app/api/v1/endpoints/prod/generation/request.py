from fastapi import APIRouter, Depends

from app.api.v1.endpoints.prod.generation.dto import StartGenerationRequest, StartGenerationResponse
from app.application.services.generation.dto import CreateGenerationRequestRequest, \
    CreateGenerationRequestResponse
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
def start_generation(
        request: StartGenerationRequest,
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
) -> StartGenerationResponse:
    generation_sec: int = service.start_generation(request.generation_request_id)
    return StartGenerationResponse(generation_sec=generation_sec)