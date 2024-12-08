from fastapi import Request
import logging

from starlette.responses import JSONResponse

from app.core.errors.error_messages import INTERNAL_SERVER_ERROR_MESSAGE

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def handle_general_exception(request: Request, exc: Exception):
    logger.error("Unhandled Exception Occurred", exc_info=exc)

    return JSONResponse(
        status_code=500,
        content={
            "error_code": "Internal Server Error",
            "message": INTERNAL_SERVER_ERROR_MESSAGE,
            "context": None
        }
    )
