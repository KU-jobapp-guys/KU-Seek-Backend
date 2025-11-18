"""RequestController implements rate-limiting for users."""

import redis
from decouple import config


class RequestController:
    """Implements rate-limiting for user requests."""

    def __init__(self, rate_limit: int = 30, interval: int = 10):
        """Initialize the RequestController."""
        self._rate_limit = rate_limit
        self._interval = interval
        self.__redis_instance = redis.Redis(
            password=config("REDIS_PASSWORD", "mysecretpw123"),
            port=6379,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30,
        )

    def request(self, user_id) -> bool:
        """Register a request for the given user_id."""
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
        """Ban a user by adding them to the blacklist set in Redis."""
        r = self.get_redis()
        r.sadd("blacklist", user_id)

    def unban_user(self, user_id: str):
        """Unban a user by removing them from the blacklist set in Redis."""
        r = self.get_redis()
        r.srem("blacklist", user_id)

    def is_banned(self, user_id: str) -> bool:
        """Check if a user is banned."""
        r = self.get_redis()
        is_ban = r.sismember("blacklist", user_id)
        return is_ban

    def get_redis(self):
        """Get the Redis instance."""
        return self.__redis_instance
