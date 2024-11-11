from typing import List
from fastapi import Depends
from app.application.services.hair_model.dto.option import GenderOption, HairStyleOption, \
    HairStyleLengthOption, HairDesignColorOption, BackgroundOption, ImageResolutionOption
from app.domain.hair_model.models.hair import Gender, HairStyle, HairStyleLength, HairDesignColor
from app.domain.hair_model.models.scene import Background, ImageResolution
from app.infrastructure.s3.s3_client import S3Client, get_s3_client
from app.infrastructure.repositories.hair_model.hair_model import GenderRepository, HairStyleRepository, \
    HairStyleLengthRepository, HairDesignRepository, HairDesignColorRepository, get_gender_repository, \
    get_hair_style_repository, get_hair_style_length_repository, get_hair_design_repository, \
    get_hair_design_color_repository, get_background_repository, get_image_resolution_repository, BackgroundRepository, \
    ImageResolutionRepository
from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_design import HairDesignInDB
from app.domain.hair_model.schemas.hair.hair_design_color import HairDesignColorInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.hair_style_length import HairStyleLengthInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB

class HairModelOptionApplicationService:
    def __init__(
            self,
            gender_repo: GenderRepository,
            hair_style_repo: HairStyleRepository,
            hair_style_length_repo: HairStyleLengthRepository,
            hair_design_repo: HairDesignRepository,
            hair_design_color_repo: HairDesignColorRepository,
            background_repo: BackgroundRepository,
            image_resolution_repo: ImageResolutionRepository,
            s3_client: S3Client
    ):
        self.gender_repo = gender_repo
        self.hair_style_repo = hair_style_repo
        self.hair_style_length_repo = hair_style_length_repo
        self.hair_design_repo = hair_design_repo
        self.hair_design_color_repo = hair_design_color_repo
        self.background_repo = background_repo
        self.image_resolution_repo = image_resolution_repo
        self.s3_client = s3_client

    # TODO: 리스트 갯수 0인 경우 에러 처리
    def get_gender_options(self) -> List[GenderOption]:
        db_gender_list: List[Gender] = self.gender_repo.get_all()
        gender_list: List[GenderInDB] = [GenderInDB.model_validate(db_gender) for db_gender in db_gender_list]
        return sorted(
            [
                GenderOption(
                    **gender.model_dump(),
                    presigned_image_url=self.s3_client.create_presigned_url(s3_key=gender.image_s3_key),
                )
                for gender in gender_list
            ],
            key=lambda x: x.order
        )

    def get_hair_style_options(self, gender_id: int) -> List[HairStyleOption]:
        db_hair_style_list: List[HairStyle] = self.hair_style_repo.get_all_by_gender(gender_id=gender_id)
        hair_style_list: List[HairStyleInDB] = [HairStyleInDB.model_validate(db_hair_style) for db_hair_style in db_hair_style_list]
        return sorted(
            [
                HairStyleOption(
                    **hair_style.model_dump(),
                    presigned_image_url=self.s3_client.create_presigned_url(s3_key=hair_style.image_s3_key)
                )
                for hair_style in hair_style_list
            ],
            key=lambda x: x.order
        )

    # TODO: 리스트 None 인 경우 에러처리
    def get_hair_style_length_options(self, hair_style_id: int) -> List[HairStyleLengthOption]:
        db_hair_style_length_list: List[HairStyleLength] = (
            self.hair_style_length_repo.get_all_by_hair_style_with_length(hair_style_id=hair_style_id)
        )
        return sorted(
            [
                HairStyleLengthOption(
                    id=db_hair_style_length.length_id,
                    title=db_hair_style_length.length.title,
                    description=db_hair_style_length.length.description,
                    presigned_image_url=self.s3_client.create_presigned_url(s3_key=db_hair_style_length.image_s3_key),
                    order=db_hair_style_length.length.order,
                )
                for db_hair_style_length in db_hair_style_length_list
            ],
            key=lambda x: x.order
        )


    def get_hair_design_color_options(self, hair_style_id: int, length_id: int) -> List[HairDesignColorOption]:
        db_hair_design: HairDesignInDB = (
            self.hair_design_repo.get_by_hair_style_and_length(hair_style_id=hair_style_id, length_id=length_id)
        )
        db_hair_design_color_list: List[HairDesignColor] = (
            self.hair_design_color_repo.get_all_by_hair_design_with_color(hair_design_id=db_hair_design.id)
        )
        return sorted(
            [
                HairDesignColorOption(
                    id=db_hair_design_color.color_id,
                    title=db_hair_design_color.color.title,
                    description=db_hair_design_color.color.description,
                    presigned_image_url=self.s3_client.create_presigned_url(s3_key=db_hair_design_color.image_s3_key),
                    order=db_hair_design_color.color.order,
                )
                for db_hair_design_color in db_hair_design_color_list
            ],
            key=lambda x: x.order
        )

    def get_background_options(self) -> List[BackgroundOption]:
        db_background_list: List[Background] = self.background_repo.get_all()
        background_list: List[BackgroundInDB] = [BackgroundInDB.model_validate(db_background) for db_background in db_background_list]
        return sorted(
            [
                BackgroundOption(
                    **background.model_dump(),
                    presigned_image_url=self.s3_client.create_presigned_url(s3_key=background.image_s3_key)
                )
                for background in background_list
            ],
            key=lambda x: x.order
        )

    def get_image_resolution_options(self) -> List[ImageResolutionOption]:
        db_image_resolution_list: List[ImageResolution] = self.image_resolution_repo.get_all()
        image_resolution_list: List[ImageResolutionInDB] = [ImageResolutionInDB.model_validate(db_image_resolution) for db_image_resolution in db_image_resolution_list]
        return sorted(
            [
                ImageResolutionOption(
                    **image_resolution.model_dump(),
                    presigned_image_url=self.s3_client.create_presigned_url(s3_key=image_resolution.image_s3_key)
                )
                for image_resolution in image_resolution_list
            ],
            key=lambda x: x.order
        )

def get_hair_model_option_application_service(
        gender_repo: GenderRepository = Depends(get_gender_repository),
        hair_style_repo: HairStyleRepository = Depends(get_hair_style_repository),
        hair_style_length_repo: HairStyleLengthRepository = Depends(get_hair_style_length_repository),
        hair_design_repo: HairDesignRepository = Depends(get_hair_design_repository),
        hair_design_color_repo: HairDesignColorRepository = Depends(get_hair_design_color_repository),
        background_repo: BackgroundRepository = Depends(get_background_repository),
        image_resolution_repo: ImageResolutionRepository = Depends(get_image_resolution_repository),
        s3_client: S3Client = Depends(get_s3_client)
) -> HairModelOptionApplicationService:
    return HairModelOptionApplicationService(
        gender_repo=gender_repo,
        hair_style_repo=hair_style_repo,
        hair_style_length_repo=hair_style_length_repo,
        hair_design_repo=hair_design_repo,
        hair_design_color_repo=hair_design_color_repo,
        background_repo=background_repo,
        image_resolution_repo=image_resolution_repo,
        s3_client=s3_client
    )