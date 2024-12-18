from fastapi import APIRouter

from app.api.v1.endpoints.dev.hair_model import options
from app.api.v1.endpoints.dev.user import auth as dev_auth

from app.api.v1.endpoints.prod.generation import request, hair_model_options
from app.api.v1.endpoints.prod.image import image
from app.api.v1.endpoints.prod.user import auth as prod_auth
from app.api.v1.endpoints.prod.user import user
from app.api.v1.endpoints.prod.home import model_thumbnail
from app.api.v1.endpoints.prod.versioning import app_version
from app.api.v1.endpoints.prod.subscription import subscribe, plans

router = APIRouter()

router.include_router(options.router, prefix="/dev/hair-model", tags=['dev/hair-model'])
router.include_router(dev_auth.router, prefix="/dev/user", tags=['dev/user'])

router.include_router(request.router, prefix="/prod/generation", tags=['generation'])
router.include_router(hair_model_options.router, prefix="/prod/generation", tags=['generation'])

router.include_router(image.router, prefix="/prod/image", tags=['image'])

router.include_router(prod_auth.router, prefix="/prod/user", tags=['user'])
router.include_router(user.router, prefix="/prod/user", tags=['user'])

router.include_router(model_thumbnail.router, prefix="/prod/home", tags=['home'])

router.include_router(app_version.router, prefix="/prod/versioning", tags=['versioning'])

router.include_router(subscribe.router, prefix="/prod/subscription", tags=['subscription'])
router.include_router(plans.router, prefix="/prod/subscription", tags=['subscription'])
