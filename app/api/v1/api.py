from fastapi import APIRouter

from app.api.v1.endpoints.dev import hair, scene

router = APIRouter()

router.include_router(hair.router, prefix="/hair", tags=['hair'])
router.include_router(scene.router, prefix="/scene", tags=['scene'])

