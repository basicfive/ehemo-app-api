from fastapi import APIRouter, Depends
from typing import List

from app.application.generation.request.dto.request import GenerationRequestRequest, GenerationRequestResponse, ReferenceImageUploadUrlResponse
from app.application.user.auth import validate_user_token
from app.application.generation.request.request_generation_service import RequestGenerationService, get_request_generation_service
from app.application.generation.request.request_info_service import get_generation_request_info_service, GenerationRequestInfoService
from app.application.generation.request.dto.request_info import GenerationRequestInfo, GenerationRequestInfoPreview

router = APIRouter()

@router.get("/calculate-token-cost", response_model=int, status_code=200)
def calculate_token_cost(
    is_high_res: bool,
    is_user_hair_model: bool,
    _: int = Depends(validate_user_token),
    service: RequestGenerationService = Depends(get_request_generation_service)
) -> int:
    return service.calculate_token_cost(is_high_res, is_user_hair_model)

@router.get("/reference-image-upload-url")
def get_reference_image_upload_url(
    _: int = Depends(validate_user_token),
    service: RequestGenerationService = Depends(get_request_generation_service)
) -> ReferenceImageUploadUrlResponse:
    return service.get_reference_image_upload_url()

@router.post("/request")
async def generation_request(
    request: GenerationRequestRequest,
    user_id: int = Depends(validate_user_token),
    service: RequestGenerationService = Depends(get_request_generation_service)
) -> GenerationRequestResponse:
    return await service.request_generation(request, user_id)

@router.get("/request-info-previews")
def get_generation_request_info_previews(
    user_id: int = Depends(validate_user_token),
    service: GenerationRequestInfoService = Depends(get_generation_request_info_service)
) -> List[GenerationRequestInfoPreview]:
    return service.get_all_user_generation_request_preview(user_id)

@router.get("/request-info/{generation_request_id}")
def get_generation_request_info(
    generation_request_id: int,
    user_id: int = Depends(validate_user_token),
    service: GenerationRequestInfoService = Depends(get_generation_request_info_service)
) -> GenerationRequestInfo:
    return service.get_generated_request_info(generation_request_id, user_id)

@router.post("/request-info/{generation_request_id}/favorite", status_code=200)
def update_request_is_favorite(
    generation_request_id: int,
    is_favorite: bool,
    user_id: int = Depends(validate_user_token),
    service: GenerationRequestInfoService = Depends(get_generation_request_info_service)
) -> None:
    service.update_request_is_favorite(generation_request_id, user_id, is_favorite)