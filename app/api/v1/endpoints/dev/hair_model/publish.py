# from fastapi import APIRouter, status, Depends
#
# from app.application.services.hair_model.hair_model_publish import HairModelPublishApplicationService, \
#     get_hair_model_publish_service
#
# router = APIRouter()
#
# # api/v1/dev/hair-model
#
# @router.post("/publish", status_code=status.HTTP_200_OK)
# def hair_model_option_publish(
#         service: HairModelPublishApplicationService = Depends(get_hair_model_publish_service)
# ):
#     service.publish()
