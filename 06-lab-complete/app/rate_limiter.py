import hashlib
import uuid
from fastapi import HTTPException
from app.config import settings
from app.redis_client import r

SCRIPT = """
local t = redis.call('TIME')
local now = tonumber(t[1]) + tonumber(t[2])/1000000
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now-60)
if redis.call('ZCARD', KEYS[1]) >= tonumber(ARGV[1]) then return 0 end
redis.call('ZADD', KEYS[1], now, ARGV[2])
redis.call('EXPIRE', KEYS[1], 60)
return 1
"""
def check_rate_limit(key: str) -> None:
    name = "rate:" + hashlib.sha256(key.encode()).hexdigest()
    if not r.eval(SCRIPT, 1, name, settings.rate_limit_per_minute, uuid.uuid4().hex):
        raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": "60"})
