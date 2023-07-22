
import time
from fastapi import FastAPI, Request
import datetime
from datetime import timedelta
from api import middleware_api
from contextlib import asynccontextmanager
from common.utils.init_config import save_configuration
from common.utils.scheduler_helper import TriggerHTTP, scheduler
from common.utils.file_helper import delete_dir
import os
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# save configuration to redis when start middleware
@asynccontextmanager
async def lifespan(app: FastAPI):

    path = f"{os.getcwd()}/logs"

    scheduler.add_job(delete_dir, 'cron', day_of_week='fri', 
                      hour=0, minute=0, 
                      args=[path],
                      start_date=datetime.datetime.today())
    
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