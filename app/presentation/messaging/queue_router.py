# from app.core.config import rabbit_mq_settings
# from app.presentation.messaging.routers.base_router import BaseRouter
# from app.presentation.messaging.routers.training_router import TrainingQueueRouter
# from app.presentation.messaging.routers.inference_router import InferenceQueueRouter
# from app.presentation.messaging.routers.upscale_router import UpscaleQueueRouter

# class QueueRouter:
#     """큐 이름에 따라 적절한 핸들러를 반환"""
#     _handlers = {
#         rabbit_mq_settings.RABBITMQ_TRAINING_CONSUME: TrainingQueueRouter(),
#         rabbit_mq_settings.RABBITMQ_INFERENCE_CONSUME: InferenceQueueRouter(),
#         rabbit_mq_settings.RABBITMQ_UPSCALE_CONSUME: UpscaleQueueRouter(),
#     }

#     @classmethod
#     def get_handler(cls, queue_name: str) -> BaseRouter:
#         handler = cls._handlers.get(queue_name)
#         if not handler:
#             raise ValueError(f"No handler registered for queue: {queue_name}")
#         return handler