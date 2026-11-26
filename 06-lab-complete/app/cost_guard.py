from datetime import datetime, timezone
from fastapi import HTTPException
from app.config import settings
from app.redis_client import r
PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006

def keys():
    now = datetime.now(timezone.utc)
    return "cost:day:" + now.strftime("%Y-%m-%d"), "cost:month:" + now.strftime("%Y-%m")

def check_budget() -> None:
    day, month = r.mget(keys())
    if float(day or 0) >= settings.daily_budget_usd or float(month or 0) >= settings.monthly_budget_usd:
        raise HTTPException(402, "Budget exhausted")

def record_cost(input_tokens: int, output_tokens: int) -> float:
    cost = input_tokens / 1000 * PRICE_INPUT_PER_1K + output_tokens / 1000 * PRICE_OUTPUT_PER_1K
    with r.pipeline() as pipe:
        for key, ttl in zip(keys(), (172800, 5356800)):
            pipe.incrbyfloat(key, cost)
            pipe.expire(key, ttl)
        pipe.execute()
    return cost
