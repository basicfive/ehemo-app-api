from fastapi import APIRouter, Depends

from app.application.services.generation.dto.query import GenerationRequestStatusResponse
from app.application.services.generation.dto.request import CreateGenerationRequestRequest, \
    GenerationRequestDetails, GenerationRequestResponse, UpdateGenerationRequestRequest
from app.application.services.generation.query import GenerationRequestQueryService, \
    get_generation_request_query_service
from app.application.services.generation.request import RequestGenerationApplicationService, \
    get_request_generation_application_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# api/v1/prod/generation/

@router.post("")
async def request_generation(
        request: CreateGenerationRequestRequest,
        user_id: int = Depends(validate_user_token),
        service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
) -> GenerationRequestResponse:
    return await service.request_generation(request, user_id)

@router.get("/{generation_request_id}/details")
def get_generation_request_details(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: GenerationRequestQueryService = Depends(get_generation_request_query_service)
) -> GenerationRequestDetails:
    return service.get_generated_request_details(generation_request_id, user_id)

@router.get("/{generation_request_id}/status")
def get_generation_request_status(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: GenerationRequestQueryService = Depends(get_generation_request_query_service)
) -> GenerationRequestStatusResponse:
    return service.get_generation_request_status(generation_request_id, user_id)

# @router.post("")
# def create_generation_request(
#         request: CreateGenerationRequestRequest,
#         user_id: int = Depends(validate_user_token),
#         service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
# ) -> GenerationRequestDetails:
#     return service.create_generation_request(request, user_id)
#
# @router.patch("/{generation_request_id}")
# def update_generation_request(
#         generated_request_id: int,
#         request: UpdateGenerationRequestRequest,
#         user_id: int = Depends(validate_user_token),
#         service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
# ) -> GenerationRequestDetails:
#     return service.update_generation_request(generated_request_id, request, user_id)
#
# @router.post("/{generation_request_id}/start")
# async def start_generation(
#         generation_request_id: int,
#         user_id: int = Depends(validate_user_token),
#         service: RequestGenerationApplicationService = Depends(get_request_generation_application_service)
# ) -> GenerationRequestResponse:
#     return await service.start_generation(generation_request_id, user_id)

