"""RequestController implements rate-limiting for users."""
import redis
import threading


class RequestController:
    def __init__(self, rate_limit:int = 30, interval: int = 10):
        self._rate_limit = rate_limit
        self._interval = interval
        self.__redis_instance = redis.Redis(
            host='localhost',
            password="admin",
            port=6379,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30,)

    def request(self, user_id) -> bool:
        if self.is_banned(user_id):
            return False
        key = f"request:{user_id}"
        r = self.get_redis()
        count = r.incr(key)
        if count == 1:
            r.expire(key, self._interval)
        if count > self._rate_limit:
            self.ban_user(user_id)
            return False
        return True

    def ban_user(self, user_id: str):
        r = self.get_redis()
        r.sadd("blacklist", user_id)

    def unban_user(self, user_id: str):
        r = self.get_redis()
        r.srem("blacklist", user_id)

    def is_banned(self, user_id: str) -> bool:
        r = self.get_redis()
        is_ban = r.sismember("blacklist", user_id)
        return is_ban

    def get_redis(self):
        return self.__redis_instance
