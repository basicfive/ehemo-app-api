from typing import List

from app.core.constants import SINGLE_INFERENCE_IMAGE_CNT
from app.core import utils
from app.schemas.generation.generation_request import GenerationRequestInDB
from app.schemas.generation.image_generation_job import ImageGenerationJobCreate
from app.schemas.hair.hair_variant_model import HairVariantModelInDB
from app.schemas.scene.posture_and_clothing import PostureAndClothingInDB
from app.services.generation import GenerationRequestService, ImageGenerationJobService
from app.services.hair import HairVariantModelService
from app.services.image import GeneratedImageService, GeneratedImageGroupService
from app.services.scene import PostureAndClothingService


class GenerationInferenceUseCase:
    def __init__(
            self,
            generation_request_service: GenerationRequestService,
            image_generation_job_service: ImageGenerationJobService,
            generated_image_service: GeneratedImageService,
            generated_image_group_service: GeneratedImageGroupService,
            hair_variant_model_service: HairVariantModelService,
            posture_and_clothing_service: PostureAndClothingService
    ):
        self.generation_request_service = generation_request_service
        self.image_generation_job_service = image_generation_job_service
        self.generated_image_service = generated_image_service
        self.generated_image_group_service = generated_image_group_service
        self.hair_variant_model_service = hair_variant_model_service
        self.posture_and_clothing_service = posture_and_clothing_service

    def start_generation(self, generation_request_id: int):
        generation_request: GenerationRequestInDB = self.generation_request_service.get(generation_request_id)
        pass

    def _create_image_generation_job(self, generation_request: GenerationRequestInDB):
        hair_variant_model: HairVariantModelInDB = self.hair_variant_model_service.get(generation_request.hair_variant_model_id)
        posture_and_clothing_list: List[PostureAndClothingInDB] = (
            self.posture_and_clothing_service.get_random_posture_and_clothing(limit=SINGLE_INFERENCE_IMAGE_CNT)
        )

        # prompt_list: List[str] = [
        #     utils.create_prompt(
        #         gender_prompt="women" if hair_variant_model.gender_id
        #         length_prompt: str,
        #         color_prompt: str,
        #         posture_and_clothing_prompt: str,
        #         background_prompt: str,
        #         lora_model_prompt: str
        #     )
        #     for
        # ]


        # for _ in range(SINGLE_INFERENCE_IMAGE_CNT):
        #     image_generation_job_create = ImageGenerationJobCreate(
        #         prompt:
        #         distilled_cfg_scale: float
        #         width: int
        #         height: int
        #         generation_request_id: int
        #     )


        pass


    def _create_generated_image_group(self):
        pass

    def _create_generated_images(self):
        pass

