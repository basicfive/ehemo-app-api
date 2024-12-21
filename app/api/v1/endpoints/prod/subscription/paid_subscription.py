from fastapi import APIRouter, status, Depends, Request, HTTPException
from fastapi.security import HTTPBearer
from pydantic import ValidationError

from app import revenuecat_settings
from app.application.services.subscription.dto.revenue_cat.event import *
from app.application.services.subscription.paid_subscription import PaidSubscriptionApplicationService, \
    get_paid_subscription_application_service

router = APIRouter()
security = HTTPBearer()

async def verify_webhook_auth(request: Request):
    """웹훅 Authorization 헤더 검증"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if auth_header != revenuecat_settings.AUTHORIZATION_HEADER_UUID:
        raise HTTPException(status_code=401, detail="Invalid authorization token")

    return auth_header

# revenue cat webhook
@router.post("/revenuecat/webhook", status_code=status.HTTP_200_OK)
async def handle_revenuecat_webhook(
       request: Request,
       auth_token: str = Depends(verify_webhook_auth),
       service: PaidSubscriptionApplicationService = Depends(get_paid_subscription_application_service),
):
   payload = await request.json()
   print("webhook payload : ")
   print(payload)
   try:
       # EventParser를 사용해 직접 변환
       event = EventParser.parse(payload["event"])

       # event type에 따른 핸들러 매핑
       handlers = {
           EventType.INITIAL_PURCHASE: service.handle_initial_purchase,
           EventType.CANCELLATION: service.handle_cancellation,
           EventType.UNCANCELLATION: service.handle_uncancellation,
           EventType.RENEWAL: service.handle_renewal,
           EventType.PRODUCT_CHANGE: service.handle_product_change,
           # EventType.TEST: service.handle_test_event,
           EventType.EXPIRATION: service.handle_expiration,  # 추가 필요
       }

       handler = handlers.get(event.type)
       if not handler:
           raise ValueError(f"Unsupported event type: {event.type}")

       handler(event)
       return {"status": "success"}

   except ValidationError as e:
      error_detail = f"Validation error detail: {e.errors()}"
      print(error_detail)  # 상세 에러 로깅
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=error_detail
      )
   except ValueError as e:
      error_detail = f"Value error detail: {str(e)}"
      print(error_detail)  # ValueError 로깅 추가
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=error_detail
      )