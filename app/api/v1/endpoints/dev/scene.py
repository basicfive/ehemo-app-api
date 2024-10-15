from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies.scene import get_background_service, get_posture_and_clothing_service, \
    get_image_resolution_service
from app.schemas.scene.background import BackgroundInDB, BackgroundCreate
from app.schemas.scene.image_resolution import ImageResolutionInDB, ImageResolutionCreate
from app.schemas.scene.posture_and_clothing import PostureAndClothingInDB, PostureAndClothingCreate
from app.services.scene import BackgroundService, PostureAndClothingService, ImageResolutionService

router = APIRouter()

@router.post("/backgrounds", response_model=BackgroundInDB, status_code=status.HTTP_201_CREATED)
def create_background(
        background: BackgroundCreate,
        service: BackgroundService = Depends(get_background_service)
) -> BackgroundInDB:
    return service.create(obj_in=background)

@router.post("/posture-and-clothing", response_model=PostureAndClothingInDB, status_code=status.HTTP_201_CREATED)
def create_background(
        posture_and_clothing: PostureAndClothingCreate,
        service: PostureAndClothingService = Depends(get_posture_and_clothing_service)
) -> PostureAndClothingInDB:
    return service.create(obj_in=posture_and_clothing)

@router.post("/image-resolution", response_model=ImageResolutionInDB, status_code=status.HTTP_201_CREATED)
def create_image_resolution(
        image_resolution: ImageResolutionCreate,
        service: ImageResolutionService = Depends(get_image_resolution_service)
) -> ImageResolutionInDB:
    return service.create(obj_in=image_resolution)



