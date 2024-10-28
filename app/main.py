import asyncio

from fastapi import FastAPI
import logging

from app.application.services.generation.manage_generation import handle_message
from app.core.db.base import Base, engine
from app.core.config import base_settings
from app.api.v1.api import router
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbit_mq_service = RabbitMQService()
    await rabbit_mq_service.connect()

    await rabbit_mq_service.consume(handle_message)
    try:
        yield
    finally:
        await rabbit_mq_service.close()

app = FastAPI(
    title=base_settings.PROJECT_NAME,
    openapi_url=f"{base_settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(router, prefix=base_settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status" : "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)