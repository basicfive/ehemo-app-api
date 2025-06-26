# from typing import Callable
# import json

# from app.core.enums.inference_types import InferenceType
# from app.presentation.messaging.routers.base_router import BaseRouter
# from app.application.generation.request.upscale_result_handler import handle_upscale_result
# from app.application.user_hair_style.thumbnail_generation.thumbnail_upscale_result_handler import handle_thumbnail_upscale_result
# class UpscaleQueueRouter(BaseRouter):
#     def handle(self, body: bytes) -> Callable:
#         data_dict = json.loads(body)
#         inference_type_str = data_dict.get("inference_type")
#         inference_type = InferenceType.from_string(inference_type_str)

#         if inference_type == InferenceType.NORMAL:
#             return handle_upscale_result
#         elif inference_type == InferenceType.THUMBNAIL:
#             return handle_thumbnail_upscale_result
#         else:
#             raise Exception(f"Invalid inference type: {inference_type_str}")
