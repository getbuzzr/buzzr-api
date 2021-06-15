import redis
import os
redis_client = redis.Redis(host=os.environ['REDIS_HOST'], port=6379, db=0)
REDIS_TTL = 300
