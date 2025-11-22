"""DBRateLimit is an interface to access database for rate-limiting operations."""

import redis
from decouple import config


class DBRateLimit:
    def __init__(self):
        self.__db_instance = redis.Redis(
            password=config("REDIS_PASSWORD", "mysecretpw123"),
            port=6379,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30,
        )

    def increment_requests(self, user_id: str):
        """Increment the number of requests made by the user.

        Args:
            user_id: The ID of the user.
        """
        key = f"request:{user_id}"
        return self.__db_instance.incr(key)

    def expire(self, key: str, interval: int):
        """Set an expiration time for a key.

        Args:
            key: The key to set the expiration for.
            interval: The expiration time in seconds.
        """
        self.__db_instance.expire(key, interval)

    def ban_user(self, user_id: str):
        """Ban a user from making requests.

        Args:
            user_id: The ID of the user.
        """
        self.__db_instance.sadd("blacklist", user_id)

    def unban_user(self, user_id: str):
        """Unban a user from making requests.

        Args:
            user_id: The ID of the user.
        """
        self.__db_instance.srem("blacklist", user_id)

    def is_banned(self, user_id: str) -> bool:
        """Check if a user is banned.

        Args:
            user_id: The ID of the user.

        Returns:
            True if the user is banned, False otherwise.
        """
        return self.__db_instance.sismember("blacklist", user_id)
