import logging
from firebase_admin import initialize_app, credentials, messaging

from app.core.config import oauth_setting
from app.core.errors.exceptions import FCMException

class FCMService:
    _instance = None

    def __init__(self):
        if not FCMService._instance:
            try:
                cred = credentials.Certificate(oauth_setting.FIREBASE_CREDENTIALS_PATH)
                FCMService._instance = initialize_app(cred)
                logging.info("FCM service initialized successfully")
            except Exception as e:
                logging.error(f"FCM initialization failed: {str(e)}")
                raise FCMException("FCM 서비스 초기화 실패")

    def send_message(self, token: str, title: str, body: str, data: dict = None) -> str:
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data,
                token=token,
            )
            return messaging.send(message)
        except Exception as e:
            logging.error(f"FCM sending failed: {str(e)}")
            raise FCMException("FCM 메시지 전송 실패")

    def send_multiple(
        self,
        tokens: list[str],
        title: str,
        body: str,
        data: dict = None
    ) -> messaging.BatchResponse:
        try:
            messages = [
                messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    data=data,
                    token=token,
                ) for token in tokens
            ]
            return messaging.send_all(messages)
        except Exception as e:
            logging.error(f"Multiple FCM sending failed: {str(e)}")
            raise FCMException("FCM 일괄 전송 실패")

def get_fcm_service():
    return FCMService()