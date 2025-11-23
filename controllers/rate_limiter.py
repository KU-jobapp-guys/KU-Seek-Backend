"""RateLimiter implements rate-limiting for users."""


class RateLimiter:
    """Implements rate-limiting for user requests."""

    def __init__(self, db_rate_limit, rate_limit: int = 30, interval: int = 10):
        """Initialize the RateLimiter."""
        self._rate_limit = rate_limit
        self._interval = interval
        self.__db_rate_limit = db_rate_limit

    def request(self, user_id) -> bool:
        """Register a request for the given user_id."""
        r = self.get_db()
        if r.is_banned(user_id):
            return False
        key = f"request:{user_id}"
        count = r.increment_requests(user_id)
        if count == 1:
            r.expire(key, self._interval)
        if count > self._rate_limit:
            r.ban_user(user_id)
            return False
        return True

    def ban_user(self, user_id: str):
        """Ban a user by adding them to the blacklist set in Redis."""
        r = self.get_db()
        r.ban_user(user_id)

    def unban_user(self, user_id: str):
        """Unban a user by removing them from the blacklist set in Redis."""
        r = self.get_db()
        r.unban_user(user_id)

    def is_banned(self, user_id: str) -> bool:
        """Check if a user is banned."""
        r = self.get_db()
        return r.is_banned(user_id)

    def get_db(self):
        """Get the Redis instance."""
        return self.__db_rate_limit
