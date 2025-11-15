"""RequestController implements rate-limiting for users."""
import redis
import threading
from redis.cache import CacheConfig
from redis.maint_notifications import MaintNotificationsConfig
# from app import redis_instance


class RequestController:
    def __init__(self, rate_limit:int = 300, interval: int = 60):
        self._rate_limit = rate_limit
        self._interval = interval
        self.__pool = self.__get_conn_pool()

    def request(self, user_id) -> bool | Exception:
        if self.is_banned(user_id):
            return False
        
        key = f"request:{user_id}"

        r = self.get_redis()
        count = r.incr(key)
        if count == 1:
            r.expire(key, 60)
        r.close()
        if count > self._rate_limit:
            self.ban_user(user_id)
            return False
        return True

    def ban_user(self, user_id: str):
        r = self.get_redis()
        r.sadd("blacklist", user_id)
        r.close()

    def unban_user(self, user_id: str):
        r = self.get_redis()
        r.srem("blacklist", user_id)
        r.close()

    def is_banned(self, user_id: str) -> bool:
        r = self.get_redis()
        is_ban = r.sismember("blacklist", user_id)
        r.close()
        return is_ban

    def get_redis(self):
        return redis.Redis(connection_pool=self.__pool)

    def __get_conn_pool(self):
        return redis.ConnectionPool(
            host='localhost', port=6379,
            password="admin",
            protocol=3,
            cache_config=CacheConfig(),
            decode_responses=True,
            maint_notifications_config=\
                MaintNotificationsConfig(enabled=False),
            health_check_interval=30,
            socket_timeout=2,
            max_connections=1,
            )


if __name__ == "__main__":
    requestController = RequestController()

    for i in range(200):
        requestController.request("bananaMan1")

    print(requestController.request("bananaMan1"))




