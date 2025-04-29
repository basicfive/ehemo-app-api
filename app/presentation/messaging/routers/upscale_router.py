from typing import Callable

from app.presentation.messaging.routers.base_router import BaseRouter
from app.application.generation.request.upscale_result_handler import handle_upscale_result

class UpscaleQueueRouter(BaseRouter):
    def handle(self, body: bytes) -> Callable:
        return handle_upscale_result
