import math
import os
import time
import uuid

import redis


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f'LLM rate limit exceeded. Retry in {retry_after}s.')


REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
redis_client = redis.Redis.from_url(REDIS_URL)

RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local token = ARGV[4]

redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)

local count = redis.call('ZCARD', key)

if count < limit then
    redis.call('ZADD', key, now, token)
    redis.call('PEXPIRE', key, window)
    return {1, 0}
end

local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
local wait = window - (now - tonumber(oldest[2]))

if wait < 1 then
    wait = 1
end

return {0, wait}
"""


def check_llm_rate_limit():
    now = int(time.time() * 1000)

    result = redis_client.eval(
        RATE_LIMIT_SCRIPT,
        1,
        'llm:global_rate_limit',
        now,
        60000,
        60,
        uuid.uuid4().hex,
    )

    allowed, wait_ms = result

    if not allowed:
        raise RateLimitExceeded(max(1, math.ceil(wait_ms / 1000)))