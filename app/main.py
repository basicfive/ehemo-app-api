from fastapi import FastAPI
import logging

from app.core.api.concurrent_request_middleware import ConcurrentRequestMiddleware
from app.core.db.base import Base, engine
from app.core.config import base_settings
from app.api.v1.api import router
from app.core.lifecycle import LifespanServices
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    services = LifespanServices()
    await services.initialize()

    app.state.services = services

    try:
        yield
    finally:
        await services.cleanup()

app = FastAPI(
    title=base_settings.PROJECT_NAME,
    openapi_url=f"{base_settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(ConcurrentRequestMiddleware, max_concurrent=15)
app.include_router(router, prefix=base_settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status" : "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)