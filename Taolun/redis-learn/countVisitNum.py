from redis import Redis
redis = Redis()
redis.hset("car","price",500)