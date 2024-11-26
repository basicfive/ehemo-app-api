from typing import List
from fastapi import Depends

from app.application.services.image.dto.query import GeneratedImageData, GeneratedImageGroupData
from app.core.errors.http_exceptions import ForbiddenException
from app.domain.generation.models.generation import GenerationRequest
from app.domain.generation.models.image import GeneratedImageGroup, GeneratedImage
from app.domain.generation.schemas.generated_image import GeneratedImageInDB
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupInDB
from app.domain.hair_model.models.scene import ImageResolution
from app.infrastructure.repositories.hair_model.hair_model import HairStyleRepository, get_hair_style_repository, \
    ImageResolutionRepository, get_image_resolution_repository
from app.infrastructure.s3.s3_client import S3Client, get_s3_client
from app.infrastructure.repositories.generation.generation import GeneratedImageRepository, \
    GeneratedImageGroupRepository, get_generated_image_repository, get_generated_image_group_repository, \
    GenerationRequestRepository, get_generation_request_repository


class ImageQueryApplicationService:
    def __init__(
            self,
            generated_image_repo: GeneratedImageRepository,
            generated_image_group_repo: GeneratedImageGroupRepository,
            hair_style_repo: HairStyleRepository,
            generation_request_repo: GenerationRequestRepository,
            image_resolution_repo: ImageResolutionRepository,
            s3_client: S3Client
    ):
        self.generated_image_repo = generated_image_repo
        self.generated_image_group_repo = generated_image_group_repo
        self.hair_style_repo = hair_style_repo
        self.generation_request_repo = generation_request_repo
        self.image_resolution_repo = image_resolution_repo
        self.s3_client = s3_client

    def get_generated_image_list_by_image_group(self, generated_image_group_id: int, user_id: int) -> List[GeneratedImageData]:

        # 검증 로직 - 해당 image group이 user의 것이 맞는가?
        db_generated_image_group: GeneratedImageGroup = self.generated_image_group_repo.get(generated_image_group_id)
        if db_generated_image_group.user_id != user_id:
            raise ForbiddenException()

        db_generated_image_list: List[GeneratedImage] = self.generated_image_repo.get_all_by_generate_image_group(generated_image_group_id)

        generated_image_response: List[GeneratedImageData] = []
        generation_request: GenerationRequest = self.generation_request_repo.get(db_generated_image_group.generation_request_id)
        image_resolution: ImageResolution = self.image_resolution_repo.get(generation_request.image_resolution_id)

        for db_generated_image in db_generated_image_list:
            generated_image = GeneratedImageInDB.model_validate(db_generated_image)
            generated_image_response.append(
                GeneratedImageData(
                    **generated_image.model_dump(),
                    width=image_resolution.width,
                    height=image_resolution.height,
                    image_url=self.s3_client.create_presigned_url(s3_key=generated_image.s3_key)
                )
            )
        return generated_image_response

    # TODO: 이 asset 이 user 의 소유가 맞는지 validation 하는 과정이 호출하는 위의 함수에 의존하고 있다.
    # validation 중복을 없애기 위해서 일단은 이렇게 하지만, 개선이 필요한 구조임.
    def get_generated_image_list_by_generation_request(self, generation_request_id: int, user_id: int) -> List[GeneratedImageData]:
        generated_image_group: GeneratedImageGroup = self.generated_image_group_repo.get_by_generation_request(generation_request_id)

        return self.get_generated_image_list_by_image_group(
            generated_image_group_id=generated_image_group.id,
            user_id=user_id
        )

    # 데이터 많아지면 pagination 이 적절히 필요할수도.
    def get_generated_image_group_list_by_user(self, user_id: int) -> List[GeneratedImageGroupData]:
        db_generated_image_group_list: List[GeneratedImageGroup] = self.generated_image_group_repo.get_all_by_user(user_id)

        generated_image_group_response: List[GeneratedImageGroupData] = []
        for db_generated_image_group in db_generated_image_group_list:
            generated_image_group = GeneratedImageGroupInDB.model_validate(db_generated_image_group)
            generated_image_group_response.append(
                GeneratedImageGroupData(
                    **generated_image_group.model_dump(),
                    thumbnail_image_url=self.s3_client.create_presigned_url(s3_key=generated_image_group.thumbnail_image_s3_key)
                )
            )
        generated_image_group_response.sort(key=lambda x: x.created_at, reverse=True)
        return generated_image_group_response


def get_image_query_application_service(
        generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
        generated_image_group_repo: GeneratedImageGroupRepository = Depends(get_generated_image_group_repository),
        hair_style_repo: HairStyleRepository = Depends(get_hair_style_repository),
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        image_resolution_repo: ImageResolutionRepository = Depends(get_image_resolution_repository),
        s3_client: S3Client = Depends(get_s3_client)
) -> ImageQueryApplicationService:
    return ImageQueryApplicationService(
        generated_image_repo=generated_image_repo,
        generated_image_group_repo=generated_image_group_repo,
        hair_style_repo=hair_style_repo,
        generation_request_repo=generation_request_repo,
        image_resolution_repo=image_resolution_repo,
        s3_client=s3_client
     )