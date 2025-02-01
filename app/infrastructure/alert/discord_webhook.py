import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def send_error_notification(
        webhook_url: str,
        error: Exception,
) -> bool:
    """
    에러 발생 시 Discord로 알림을 보냅니다.

    Args:
        webhook_url (str): 웹훅 주소
        error (Exception): 발생한 에러 객체

    Returns:
        bool: 전송 성공 여부
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 기본 에러 정보
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": current_time
        }

        # Discord 임베드 메시지 구성
        embed = {
            "title": "❌ 에러 발생",
            "color": 0xFF0000,  # 빨간색
            "fields": [
                {
                    "name": key.replace('_', ' ').title(),
                    "value": str(value),
                    "inline": False
                }
                for key, value in error_info.items()
            ],
            "footer": {
                "text": "자동 에러 알림 시스템"
            }
        }

        # Discord 웹훅 페이로드
        payload = {
            "embeds": [embed]
        }

        # 웹훅 전송
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 204:  # Discord 웹훅 성공 상태 코드
            logger.info("Discord 알림 전송 성공")
            return True
        else:
            logger.error(f"Discord 알림 전송 실패: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Discord 알림 전송 중 에러 발생: {str(e)}")
        return False