
import time
from fastapi import FastAPI, Request
import datetime
from api import middleware_api
from contextlib import asynccontextmanager
from common.utils.init_config import save_configuration
import logging
from business_rules.logging.logging_service import InitRotatingLog

logger = InitRotatingLog(filename="tmp", rotation_freq="S", interval=3)

# save configuration to redis when start middleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    # read the xml configuration file then write to redis
    await save_configuration()
    yield
    # task after done handling requests can be put here
app = FastAPI(lifespan=lifespan)

# middleware_api
app.include_router(
    middleware_api.router,
    prefix="/trigger",
    tags=["trigger"]
)