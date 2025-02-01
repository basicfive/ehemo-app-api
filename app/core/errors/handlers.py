from fastapi import Request
import logging

from starlette.responses import JSONResponse

from app import base_settings
from app.core.errors.error_messages import INTERNAL_SERVER_ERROR_MESSAGE
from app.infrastructure.alert.discord_webhook import send_error_notification

logger = logging.getLogger(__name__)

async def handle_general_exception(request: Request, exc: Exception):
    logger.error("Unhandled Exception Occurred", exc_info=exc)

    send_error_notification(webhook_url=base_settings.ALERT_DISCORD_WEBHOOK, error=exc)

    return JSONResponse(
        status_code=500,
        content={
            "error_code": "Internal Server Error",
            "message": INTERNAL_SERVER_ERROR_MESSAGE,
            "context": None
        }
    )
