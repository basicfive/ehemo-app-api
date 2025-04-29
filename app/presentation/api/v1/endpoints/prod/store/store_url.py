from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app import StoreUrls

router = APIRouter()

# /api/v1/prod/store/

@router.get("/ehemo")
async def redirect_to_store(request: Request):
    user_agent = request.headers.get("user-agent", "").lower()

    # iOS 기기 확인
    if any(device in user_agent for device in ["iphone", "ipad", "ipod"]):
        return RedirectResponse(url=StoreUrls.IOS)

    # 안드로이드 기기 확인
    if "android" in user_agent:
        return RedirectResponse(url=StoreUrls.ANDROID)

    # 기타 기기는 웹사이트로
    return RedirectResponse(url=StoreUrls.WEB)