import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from app.logging import configure_logging
from app.observability.langsmith import init_langsmith
from app.messaging.kafka import start_kafka, stop_kafka

from app.auth.routes import router as auth_router
from app.menu.routes import router as menu_router
from app.chat.routes import router as chat_router

configure_logging()
init_langsmith()
log = logging.getLogger("app")

app = FastAPI(default_response_class=ORJSONResponse, title="Restaurant LLM Chat API")

@app.on_event("startup")
async def _startup():
    await start_kafka()
    log.info("app.startup")

@app.on_event("shutdown")
async def _shutdown():
    await stop_kafka()
    log.info("app.shutdown")

@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    latency_ms = int((time.time() - start) * 1000)

    log.info(
        "http.request",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        },
    )
    response.headers["x-request-id"] = request_id
    return response

app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(chat_router)
