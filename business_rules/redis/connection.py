import aioredis
from pydantic import BaseSettings
from common.const import REDIS_PORT

# Connection setup
class Config(BaseSettings):
    # The default URL expects the app to run using Docker and docker-compose.
    redis_url: str = 'redis://redis:'
    redis_port: str = REDIS_PORT
    
config = Config()
redis = aioredis.from_url(config.redis_url + config.redis_port)


        