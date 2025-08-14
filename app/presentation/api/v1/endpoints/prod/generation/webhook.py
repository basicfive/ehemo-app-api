from fastapi import APIRouter, Depends
from app.application.generation.request.generation_result_handler import GenerationResultHandler, get_generation_result_handler
from app.infrastructure.runpod.dto import WebhookResponse

router = APIRouter()

@router.post("/webhook/runpod")
def generation_result_webhook(
    result: WebhookResponse,
    service: GenerationResultHandler = Depends(get_generation_result_handler),
):
    service.handle_generation_result(result)
