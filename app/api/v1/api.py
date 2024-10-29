from fastapi import APIRouter

from app.api.v1.endpoints.dev.hair_model import options
from app.api.v1.endpoints.dev.user import auth as dev_auth

from app.api.v1.endpoints.prod.generation import request, hair_model_options
from app.api.v1.endpoints.prod.image import image
from app.api.v1.endpoints.prod.user import auth as prod_auth

router = APIRouter()

router.include_router(options.router, prefix="/dev/hair-model", tags=['dev/hair-model'])
router.include_router(dev_auth.router, prefix="/dev/user", tags=['dev/user'])

router.include_router(request.router, prefix="/prod/generation", tags=['generation'])
router.include_router(hair_model_options.router, prefix="/prod/generation", tags=['generation'])
router.include_router(image.router, prefix="/prod/image", tags=['image'])
router.include_router(prod_auth.router, prefix="/prod/user", tags=['user'])
