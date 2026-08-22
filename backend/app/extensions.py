from flask_socketio import SocketIO
import redis
from config import Config

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading",
    logger=True,
    engineio_logger=True
)

redis_client = redis.Redis.from_url(
    Config.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1
)