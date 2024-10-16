from typing import List

from app.schemas.generation.generation_request import GenerationRequestCreateRequest, GenerationRequestCreateResponse, \
    GenerationRequestCreate, GenerationRequestInDB

from app.schemas.hair.hair_variant_model import HairVariantModelInDB
from app.services.generation import GenerationRequestService
from app.services.hair import ColorService
from app.services.user import UserService

from app.schemas.hair.gender import GenderInDB
from app.schemas.hair.hair_design import HairDesignInDB
from app.schemas.hair.hair_design_color import HairDesignColorInDB
from app.schemas.hair.hair_style import HairStyleInDB
from app.schemas.hair.hair_style_length import HairStyleLengthInDB
from app.schemas.scene.background import BackgroundInDB
from app.schemas.scene.image_resolution import ImageResolutionInDB
from app.services.hair import GenderService, HairStyleService, LengthService, HairStyleLengthService, HairDesignService, \
    HairDesignColorService, HairVariantModelService
from app.services.scene import BackgroundService, ImageResolutionService


class SelectOptionUseCase:
    def __init__(
            self,
            gender_service: GenderService,
            hair_style_service: HairStyleService,
            length_service: LengthService,
            hair_style_length_service: HairStyleLengthService,
            hair_design_service: HairDesignService,
            hair_design_color_service: HairDesignColorService,
            background_service: BackgroundService,
            image_resolution_service: ImageResolutionService,
    ):
        self.gender_service = gender_service
        self.hair_style_service = hair_style_service
        self.length_service = length_service
        self.hair_style_length_service = hair_style_length_service
        self.hair_design_service = hair_design_service
        self.hair_design_color_service = hair_design_color_service
        self.background_service = background_service
        self.image_resolution_service = image_resolution_service

    def get_gender_options(self) -> List[GenderInDB]:
        return self.gender_service.get_all()

    def get_hair_style_options(self, gender_id: int) -> List[HairStyleInDB]:
        return self.hair_style_service.get_all_by_gender(gender_id=gender_id)

    def get_hair_style_length_options(self, hair_style_id: int) -> List[HairStyleLengthInDB]:
        return self.hair_style_length_service.get_all_by_hair_style(hair_style_id=hair_style_id)

    def get_hair_design_color_options(self, hair_style_id: int, length_id: int) -> List[HairDesignColorInDB]:
        hair_design: HairDesignInDB = self.hair_design_service.get_all_by_hair_style_and_length(hair_style_id=hair_style_id, length_id=length_id)
        return self.hair_design_color_service.get_all_by_hair_design(hair_design_id=hair_design.id)

    def get_background_options(self) -> List[BackgroundInDB]:
        return self.background_service.get_all()

    def get_image_resolution_options(self) -> List[ImageResolutionInDB]:
        return self.image_resolution_service.get_all()


class GenerationRequestUseCase:
    def __init__(
            self,
            hair_variant_model_service: HairVariantModelService,
            generation_request_service: GenerationRequestService,
            user_service: UserService,
            gender_service: GenderService,
            hair_style_service: HairStyleService,
            length_service: LengthService,
            color_service: ColorService,
            background_service: BackgroundService,
            image_resolution_service: ImageResolutionService,
    ):
        self.hair_variant_model_service = hair_variant_model_service
        self.generation_request_service = generation_request_service
        self.user_service = user_service
        self.gender_service = gender_service
        self.hair_style_service = hair_style_service
        self.length_service = length_service
        self.color_service = color_service
        self.background_service = background_service
        self.image_resolution_service = image_resolution_service

    def create_generation_request(self, request: GenerationRequestCreateRequest) -> GenerationRequestCreateResponse:
        hair_variant_model: HairVariantModelInDB = self.hair_variant_model_service.get_by_hair_style_length_color(
            hair_style_id=request.hair_style_id,
            length_id=request.length_id,
            color_id=request.color_id
        )

        generation_request_create = GenerationRequestCreate(
            user_id=request.user_id,
            hair_variant_model_id=hair_variant_model.id,
            background_id=request.background_id,
            image_resolution_id=request.image_resolution_id
        )
        generation_request: GenerationRequestInDB = self.generation_request_service.create(obj_in=generation_request_create)

        return self._create_request_response(hair_variant_model, generation_request)

    def _create_request_response(
            self,
            hair_variant_model: HairVariantModelInDB,
            generation_request: GenerationRequestInDB
    ) -> GenerationRequestCreateResponse:

        return GenerationRequestCreateResponse(
            generation_request_id=generation_request.id,
            user=self.user_service.get(obj_id=generation_request.user_id),
            gender=self.gender_service.get(hair_variant_model.gender_id),
            hair_style=self.hair_style_service.get(hair_variant_model.hair_style_id),
            length=self.hair_style_service.get(hair_variant_model.length_id) if hair_variant_model.length_id else None,
            color=self.color_service.get(hair_variant_model.color_id),
            background=self.background_service.get(generation_request.background_id),
            image_resolution=self.image_resolution_service.get(generation_request.image_resolution_id),
        )