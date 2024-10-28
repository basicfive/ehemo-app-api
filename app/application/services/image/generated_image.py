from typing import List
from fastapi import Depends

from app.application.services.image.dto.generated_image import GeneratedImageData, GeneratedImageGroupData
from app.domain.generation.models.image import GeneratedImageGroup, GeneratedImage
from app.domain.generation.schemas.generated_image import GeneratedImageInDB
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupInDB
from app.infrastructure.s3.s3_client import S3Client, get_s3_client
from app.infrastructure.repositories.generation.generation import GeneratedImageRepository, \
    GeneratedImageGroupRepository, get_generated_image_repository, get_generated_image_group_repository

class GeneratedImageApplicationService:
    """
    TODO: CRUD를 안하는데 너무 이름을 제너럴하게 지은듯.
    ㄴ 근데 또 생성된 이미지 그룹 단위로 삭제 가능하게 할거잖아.
    생성된 이미지 조회용 서비스
    * mq 로부터 생성 결과 받아서 이미지 생성하는 로직은 generation_request 에서 관리
    """
    def __init__(
            self,
            generated_image_repo: GeneratedImageRepository,
            generated_image_group_repo: GeneratedImageGroupRepository,
            s3_client: S3Client
    ):
        self.generated_image_repo = generated_image_repo
        self.generated_image_group_repo = generated_image_group_repo
        self.s3_client = s3_client

    def get_generated_image_list_by_image_group(self, generated_image_group_id: int) -> List[GeneratedImageData]:
        db_generated_image_list: List[GeneratedImage] = self.generated_image_repo.get_all_by_generate_image_group(generated_image_group_id)

        generated_image_response: List[GeneratedImageData] = []
        for db_generated_image in db_generated_image_list:
            generated_image = GeneratedImageInDB.model_validate(db_generated_image)
            generated_image_response.append(
                GeneratedImageData(
                    **generated_image.model_dump(),
                    image_url=self.s3_client.create_presigned_url(s3_key=generated_image.s3_key)
                )
            )
        return generated_image_response

    # pagination 이 적절히 필요할수도.
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
        return generated_image_group_response


def get_generated_image_application_service(
        generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
        generated_image_group_repo: GeneratedImageGroupRepository = Depends(get_generated_image_group_repository),
        s3_client: S3Client = Depends(get_s3_client)
) -> GeneratedImageApplicationService:
    return GeneratedImageApplicationService(
        generated_image_repo=generated_image_repo,
        generated_image_group_repo=generated_image_group_repo,
        s3_client=s3_client
    )