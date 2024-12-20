from fastapi import APIRouter, status, Depends, Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from app import revenuecat_settings
from app.application.services.subscription.dto.revenue_cat.event import *
from app.application.services.subscription.paid_subscription import PaidSubscriptionApplicationService, \
    get_paid_subscription_application_service

router = APIRouter()
security = HTTPBearer()

def verify_webhook_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """웹훅 Authorization 헤더 검증"""
    if credentials.credentials != revenuecat_settings.AUTHORIZATION_HEADER_UUID:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token"
        )
    return credentials.credentials

# revenue cat webhook
@router.post("/revenuecat/webhook", status_code=status.HTTP_200_OK)
# auth 검증 로직 추가해야함.
async def handle_revenuecat_webhook(
        request: Request,
        auth_token: str = Depends(verify_webhook_auth),
        service: PaidSubscriptionApplicationService = Depends(get_paid_subscription_application_service),
):
    payload = await request.json()
    try:
        webhook_event = WebhookEvent.from_payload(payload)
        event = webhook_event.parse_event()

        if isinstance(event, InitialPurchase):
            service.handle_initial_purchase(event)

        elif isinstance(event, Cancellation):
            service.handle_cancellation(event)

        elif isinstance(event, Uncancellation):
            service.handle_uncancellation(event)

        elif isinstance(event, Renewal):
            service.handle_renewal(event)

        elif isinstance(event, ProductChange):
            service.handle_product_change(event)

        else:
            raise ValueError(f"Unsupported event type: {event.type}")

        return {"status": "success"}

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload format: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
