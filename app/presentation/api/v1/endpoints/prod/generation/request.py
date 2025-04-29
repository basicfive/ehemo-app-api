from fastapi import APIRouter, Depends

from app.application.generation.request.dto.request import GenerationRequestRequest, GenerationRequestResponse
from app.application.user.auth import validate_user_token
from app.application.generation.request.request_generation_service import RequestGenerationService, get_request_generation_service

router = APIRouter()


@router.post("/request")
async def generation_request(
    request: GenerationRequestRequest,
    user_id: int = Depends(validate_user_token),
    service: RequestGenerationService = Depends(get_request_generation_service)
) -> GenerationRequestResponse:
    return await service.request_generation(request, user_id)