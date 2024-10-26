# def get_image_by_group(
#         generated_image_group_id: int,
#         service: GeneratedImageApplicationService = Depends(get_generated_image_application_service)
# ) -> List[GeneratedImageInDB]:
#     return service.get_generated_image_list_by_image_group(generated_image_group_id=generated_image_group_id)
#
# @router.get("/image_groups")
# def get_image_groups_by_user(

from pydantic import BaseModel

class GeneratedImageByGroupRequest(BaseModel):
