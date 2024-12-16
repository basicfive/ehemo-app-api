from fastapi import APIRouter, status

from app.core.enums.subscription_event import RevenueCatEventType

router = APIRouter()

# /prod/subscription/

# @router.post("/webhook/revenuecat", status_code=status.HTTP_200_OK)
# # auth 검증 로직 추가해야함.
# def handle_revenuecat_webhook(
#         event_type: str,
#
# ):
#     event = RevenueCatEventType.from_str(event_type)
#
#     match event:
#         case RevenueCatEventType.INITIAL_PURCHASE:
#
#         case RevenueCatEventType.RENEWAL:
#
#         case RevenueCatEventType.EXPIRATION:
