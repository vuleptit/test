
import time
from fastapi import FastAPI, Request
import datetime
from api import middleware_api
from contextlib import asynccontextmanager
from common.utils.init_config import save_configuration
from os.path import abspath, basename, dirname, join, normpath, realpath

# save configuration to redis when start middleware
@asynccontextmanager
async def lifespan(app: FastAPI):

    # print(normpath(__file__))

    # # read the xml configuration file then write to redis
    # await save_configuration()
    yield
    # handler.doRollover()
    # task after done handling requests can be put here
app = FastAPI(lifespan=lifespan)

# middleware_api
app.include_router(
    middleware_api.router,
    prefix="/trigger",
    tags=["trigger"]
)