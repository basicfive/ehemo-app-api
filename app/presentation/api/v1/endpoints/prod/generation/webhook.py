from fastapi import APIRouter, Depends
from app.application.generation.request.generation_result_handler import GenerationResultHandler, get_generation_result_handler
from app.application.generation.request.upscale_result_handler import UpscaleResultHandler, get_upscale_result_hander
from app.infrastructure.replicate.dto import ReplicateResponse

router = APIRouter()

@router.post("/webhook/generation")
def generation_result_webhook(
    result: ReplicateResponse,
    service: GenerationResultHandler = Depends(get_generation_result_handler),
):
    service.handle_generation_result(result)

@router.post("/webhook/upscale")
def upscale_result_webhook(
    result: ReplicateResponse,
    service: UpscaleResultHandler = Depends(get_upscale_result_hander),
):
    service.handle_upscale_result(result)