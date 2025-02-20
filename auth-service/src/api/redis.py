import os
import redis.asyncio as redis

redis_client = redis.Redis("redis")

async def add_key_value_redis(key, value):
    await redis_client.set(key, value)
    if expire:
        await redis_client.expire(key, expire)

async def get_value_redis(key):
    return await redis_client.get(key)

async def delete_key_redis(key):
    await redis_client.delete(key)
