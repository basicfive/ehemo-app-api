from fastapi import APIRouter

from app.api.v1.endpoints.dev.hair_model import options
from app.api.v1.endpoints.prod.generation import request, hair_model_options
from app.api.v1.endpoints.prod.image import image

router = APIRouter()

router.include_router(options.router, prefix="/dev/hair-model", tags=['hair-model'])

router.include_router(request.router, prefix="/prod/generation", tags=['generation'])
router.include_router(hair_model_options.router, prefix="/prod/generation", tags=['generation'])


router.include_router(image.router, prefix="/prod/image", tags=['image'])
