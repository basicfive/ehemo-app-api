import threading

from fastapi import FastAPI
import logging

from app.application.services.generation.manage_generation import handle_massage
from app.core.db.base import Base, engine
from app.core.config import settings
from app.api.v1.api import router
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     initialize_rabbit_mq(handle_massage)
#     yield

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rabbit_mq = RabbitMQService()

    # 컨슈머 스레드 시작
    def start_consumer():
        app.state.rabbit_mq.consume(handle_massage)

    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

    yield

    app.state.rabbit_mq.cleanup()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status" : "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)