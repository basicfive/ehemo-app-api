from fastapi import APIRouter, Depends, status

from app.application.services.generation.dto.query import GenerationRequestStatus, GenerationRequestDetails, \
    GenerationRequestStatusWithDetails
from app.application.services.generation.dto.request import CreateGenerationRequestRequest, \
    GenerationRequestResponse
from app.application.services.generation.query import GenerationRequestQueryService, \
    get_generation_request_query_service
from app.application.services.generation.request import RequestGenerationApplicationService, \
    get_request_generation_application_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# api/v1/prod/generation/

@router.post("", response_model=GenerationRequestStatusWithDetails, status_code=status.HTTP_200_OK)
async def request_generation(
        request: CreateGenerationRequestRequest,
        user_id: int = Depends(validate_user_token),
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
) -> GenerationRequestStatusWithDetails:
    return await service.request_generation(request, user_id)

@router.post("/{generation_request_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_generation(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
):
    service.cancel_generation(generation_request_id, user_id)

@router.post("/{generation_request_id}/confirm_result", status_code=status.HTTP_200_OK)
def cancel_generation(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
):
    service.confirm_generation_result(generation_request_id, user_id)


@router.get("/{generation_request_id}/details", response_model=GenerationRequestDetails, status_code=status.HTTP_200_OK)
def get_generation_request_details(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: GenerationRequestQueryService = Depends(get_generation_request_query_service)
) -> GenerationRequestDetails:
    return service.get_generated_request_details(generation_request_id, user_id)

@router.get("/{generation_request_id}/status", response_model=GenerationRequestStatus, status_code=status.HTTP_200_OK)
def get_generation_request_status(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: GenerationRequestQueryService = Depends(get_generation_request_query_service)
) -> GenerationRequestStatus:
    return service.get_generation_request_status(generation_request_id, user_id)

@router.get("/latest_with_details", response_model=GenerationRequestStatusWithDetails, status_code=status.HTTP_200_OK)
def get_generation_request_status_with_details(
        user_id: int = Depends(validate_user_token),
        service: GenerationRequestQueryService = Depends(get_generation_request_query_service)
) -> GenerationRequestStatusWithDetails:
    return service.get_latest_generation_request_status_with_details(user_id)

