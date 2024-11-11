from fastapi import Depends
from typing import Optional, List
from app.application.query.dto.hair_model_details import HairModelDetails
from app.domain.hair_model.models.hair import HairVariantModel, SpecificColor, Length, HairStyle
from app.domain.hair_model.models.scene import PostureAndClothing
from app.infrastructure.repositories.hair_model.hair_model import HairVariantModelRepository, ColorRepository, \
    SpecificColorRepository, LengthRepository, HairStyleRepository, GenderRepository, LoRAModelRepository, \
    BackgroundRepository, ImageResolutionRepository, PostureAndClothingRepository, get_hair_variant_model_repository, \
    get_color_repository, get_specific_color_repository, get_length_repository, get_hair_style_repository, \
    get_background_repository, get_gender_repository, get_image_resolution_repository, get_lora_model_repository, \
    get_posture_and_clothing_repository

"""
DTO 에 적어둔 것과 같은 문제인데, 여기서 엔티티를 schema로 감싸서 보내야하는지에 대한 의문이 있다.
"""

class HairModelQueryService:
    """
    여러 repo를 사용해서 복잡하게 처리되는 query 로직을 처리하는 서비스.
    application service 가 의존할 수 있으며, presentation 쪽에서 직접적으로 접근할 수 없다.
    모델 엔티티 혹은 DTO 를 반환함.
    """
    def __init__(
            self,
            hair_variant_model_repo: HairVariantModelRepository,
            color_repo: ColorRepository,
            specific_color_repo: SpecificColorRepository,
            length_repo: LengthRepository,
            hair_style_repo: HairStyleRepository,
            gender_repo: GenderRepository,
            background_repo: BackgroundRepository,
            image_resolution_repo: ImageResolutionRepository,
            lora_model_repo: LoRAModelRepository,
            posture_and_clothing_repo: PostureAndClothingRepository
    ):
        self.hair_variant_model_repo = hair_variant_model_repo
        self.color_repo = color_repo
        self.specific_color_repo = specific_color_repo
        self.length_repo = length_repo
        self.hair_style_repo = hair_style_repo
        self.gender_repo = gender_repo
        self.background_repo = background_repo
        self.image_resolution_repo = image_resolution_repo
        self.lora_model_repo = lora_model_repo
        self.posture_and_clothing_repo = posture_and_clothing_repo

    def get_hair_variant_model_by_hair_style_length_color(
            self,
            hair_style_id: int,
            length_id: Optional[int],
            color_id: int
    ) -> HairVariantModel:
        return self.hair_variant_model_repo.get_by_hair_style_length_color(
            hair_style_id=hair_style_id,
            length_id=length_id,
            color_id=color_id
        )

    def get_hair_model_details(
            self,
            hair_variant_model_id: int,
            background_id: int,
            image_resolution_id: int
    ) -> HairModelDetails:
        hair_variant_model: HairVariantModel = self.hair_variant_model_repo.get(hair_variant_model_id)
        specific_color_list: List[SpecificColor] = self.specific_color_repo.get_all_by_color_limit(hair_variant_model.color_id)
        length = self.length_repo.get(hair_variant_model.length_id) if hair_variant_model.length_id else None
        return HairModelDetails(
            gender=self.gender_repo.get(hair_variant_model.gender_id),
            hair_style=self.hair_style_repo.get(hair_variant_model.hair_style_id),
            length=length,
            color=self.color_repo.get(hair_variant_model.color_id),
            specific_color_list=specific_color_list,
            lora_model=self.lora_model_repo.get(hair_variant_model.lora_model_id),
            background=self.background_repo.get(background_id),
            image_resolution=self.image_resolution_repo.get(image_resolution_id)
        )

    def get_random_posture_and_clothing(self, limit: int) -> List[PostureAndClothing]:
        return self.posture_and_clothing_repo.get_random_records(limit=limit)

    def get_length_by_hair_style(self, hair_style_id: int) -> Length:
        hair_style: HairStyle = self.hair_style_repo.get(obj_id=hair_style_id)
        return self.length_repo.get(hair_style.length_id)

    def get_hair_style_by_hair_variant_model(self, hair_variant_model_id: int) -> HairStyle:
        hair_variant_model: HairVariantModel = self.hair_variant_model_repo.get(hair_variant_model_id)
        return self.hair_style_repo.get(hair_variant_model.hair_style_id)


# dependency
def get_hair_model_query_service(
        hair_variant_model_repo: HairVariantModelRepository = Depends(get_hair_variant_model_repository),
        color_repo: ColorRepository = Depends(get_color_repository),
        specific_color_repo: SpecificColorRepository = Depends(get_specific_color_repository),
        length_repo: LengthRepository = Depends(get_length_repository),
        hair_style_repo: HairStyleRepository = Depends(get_hair_style_repository),
        gender_repo: GenderRepository = Depends(get_gender_repository),
        background_repo: BackgroundRepository = Depends(get_background_repository),
        image_resolution_repo: ImageResolutionRepository = Depends(get_image_resolution_repository),
        lora_model_repo: LoRAModelRepository = Depends(get_lora_model_repository),
        posture_and_clothing_repo: PostureAndClothingRepository = Depends(get_posture_and_clothing_repository)
) -> HairModelQueryService:
    return HairModelQueryService(
        hair_variant_model_repo=hair_variant_model_repo,
        color_repo=color_repo,
        specific_color_repo=specific_color_repo,
        length_repo=length_repo,
        hair_style_repo=hair_style_repo,
        gender_repo=gender_repo,
        background_repo=background_repo,
        image_resolution_repo=image_resolution_repo,
        lora_model_repo=lora_model_repo,
        posture_and_clothing_repo=posture_and_clothing_repo
    )
