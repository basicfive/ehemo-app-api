from typing import List, Optional, Dict
import logging
from firebase_admin import messaging, credentials, initialize_app
import firebase_admin

from app.core.config import oauth_setting
from app.core.errors.exceptions import FCMException

logger = logging.getLogger()

class FCMService:
    _instance = None

    def __init__(self):
        try:
            cred = credentials.Certificate(oauth_setting.FIREBASE_CREDENTIALS_PATH)
            if not firebase_admin._apps:
                initialize_app(cred)
        except Exception as e:
            raise FCMException(context=f"Failed to initialize Firebase Admin: {str(e)}")

    def send_to_token(
            self,
            token: str,
            title: str,
            body: str,
            category: Optional[str] = None,  # 카테고리(click_action/category)
            identifier: Optional[str] = None,  # 식별자(tag/thread_id)
            data: Optional[Dict[str, str]] = None
    ) -> dict:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        click_action=category,
                        tag=identifier,
                        priority='max',  # 추가: 알림 우선순위
                        visibility='public'  # 추가: 잠금화면에서도 표시
                    ) if category or identifier else None
                ),
                apns=messaging.APNSConfig(
                    headers={'apns-priority': '10'},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body,
                            ),
                            category=category,
                            thread_id=identifier
                        )
                    )
                ) if category or identifier else None,
                data=data or {},
                token=token,
            )

            logger.info(f"sending fcm message... title: {title}, token: {token[:10]}")
            response = messaging.send(message)
            return {"success": True, "message_id": response}
        except Exception as e:
            raise FCMException(context=f"Failed to send FCM message: {str(e)}")

    def send_to_tokens(
            self,
            tokens: List[str],
            title: str,
            body: str,
            data: Optional[Dict[str, str]] = None
    ) -> dict:
        """
        Send FCM message to multiple device tokens
        """
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )

            response = messaging.send_each_for_multicast(message)
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
            }
        except Exception as e:
            raise FCMException(context=f"Failed to send FCM messages: {str(e)}")

    def send_to_topic(
            self,
            topic: str,
            title: str,
            body: str,
            data: Optional[Dict[str, str]] = None
    ) -> dict:
        """
        Send FCM message to a topic
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )

            response = messaging.send(message)
            return {"success": True, "message_id": response}
        except Exception as e:
            raise FCMException(f"Failed to send FCM message to topic: {str(e)}")

    def subscribe_to_topic(
            self,
            tokens: List[str],
            topic: str
    ) -> dict:
        """
        Subscribe devices to a topic
        """
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
            }
        except Exception as e:
            raise FCMException(context=f"Failed to subscribe to topic: {str(e)}")

def get_fcm_service():
    return FCMService()