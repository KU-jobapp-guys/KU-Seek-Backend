"""RateLimiter implements rate-limiting for users."""


class RateLimiter:
    """Implements rate-limiting for user requests."""

    def __init__(self, db_rate_limit, rate_limit: int = 30, interval: int = 10):
        """Initialize the RateLimiter."""
        self._rate_limit = rate_limit
        self._interval = interval
        self.__db_rate_limit = db_rate_limit

        self._login_rate_limit = 5
        self._login_interval = 15 * 60  # 15 minutes

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

    def attempt_login(self, ip_address: str) -> bool:
        """Register a login attempt for rate-limiting purposes."""
        r = self.get_db()
        key = "login_attempts:" + ip_address
        count = r.increment_requests(key)
        if count == 1:
            r.expire(key, self._login_interval)
        if count > self._login_rate_limit:
            return False
        return True
