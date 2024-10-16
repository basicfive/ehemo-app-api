from app.services.generation import GenerationRequestService, ImageGenerationJobService
from app.services.image import GeneratedImageService, GeneratedImageGroupService


class GenerationInferenceUseCase:
    def __init__(
            self,
            generation_request_service: GenerationRequestService,
            image_generation_job_service: ImageGenerationJobService,
            generated_image_service: GeneratedImageService,
            generated_image_group_service: GeneratedImageGroupService
    ):
        self.generation_request_service = generation_request_service
        self.image_generation_job_service = image_generation_job_service
        self.generated_image_service = generated_image_service
        self.generated_image_group_service = generated_image_group_service

    def start_generation(self, generation_request_id: int):

        pass

    def _create_image_generation_job(self):
        pass

    def _create_generated_image_group(self):
        pass

    def _create_generated_images(self):
        pass

