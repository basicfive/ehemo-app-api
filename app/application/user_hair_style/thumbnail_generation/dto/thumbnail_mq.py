# from app.application.generation.request.dto.generation_mq import GenerationPublishMessage, GenerationConsumeMessage
# from app.application.generation.request.dto.upscale_mq import UpscalePublishMessage, UpscaleConsumeMessage
# from app.core.enums.inference_types import InferenceType

# class ThumbnailGenerationPublishMessage(GenerationPublishMessage):
#     inference_type: InferenceType = InferenceType.THUMBNAIL
#     training_job_id: int

# class ThumbnailGenerationConsumeMessage(GenerationConsumeMessage):
#     inference_type: InferenceType = InferenceType.THUMBNAIL
#     training_job_id: int

# class ThumbnailUpscalePublishMessage(UpscalePublishMessage):
#     inference_type: InferenceType = InferenceType.THUMBNAIL
#     training_job_id: int

# class ThumbnailUpscaleConsumeMessage(UpscaleConsumeMessage):
#     inference_type: InferenceType = InferenceType.THUMBNAIL
#     training_job_id: int