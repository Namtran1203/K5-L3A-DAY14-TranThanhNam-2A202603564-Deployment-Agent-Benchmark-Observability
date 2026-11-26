import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from redis import RedisError
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit
from app.cost_guard import check_budget, record_cost
from app.redis_client import r, redis_healthy
from utils.mock_llm import ask as llm_ask

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "level": record.levelname, "message": record.getMessage()})
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("agent")
logger.handlers = [handler]
logger.setLevel(logging.INFO)
logger.propagate = False

@asynccontextmanager
async def lifespan(app):
    logger.info("startup")
    yield
    r.close()
    logger.info("shutdown complete")

app = FastAPI(title="Production AI Agent", lifespan=lifespan)

@app.middleware("http")
async def log_request(request: Request, call_next):
    started = time.monotonic()
    response = await call_next(request)
    logger.info(json.dumps({"path": request.url.path, "status": response.status_code, "ms": round((time.monotonic()-started)*1000, 2)}))
    return response

@app.exception_handler(RedisError)
async def redis_error(request, exc):
    logger.error("Redis unavailable")
    return JSONResponse(status_code=503, content={"detail": "Dependency unavailable"})

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    if not redis_healthy():
        raise HTTPException(503, "Redis unavailable")
    return {"status": "ready"}

@app.post("/ask")
def ask(body: AskRequest, key: str = Depends(verify_api_key)):
    check_rate_limit(key)
    check_budget()
    answer = llm_ask(body.question)
    cost = record_cost(max(1, len(body.question)//4), max(1, len(answer)//4))
    return {"question": body.question, "answer": answer, "cost_usd": cost}
