from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def general_exception_handler(request: Request, exc: Exception):
    error_message = f"Unhandled error occurred: {str(exc)}"
    logger.error(error_message, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message", "An internal server error occurred"}
    )