from fastapi import FastAPI
import datetime
from datetime import timedelta
from api import middleware_api
from contextlib import asynccontextmanager
from common.utils.scheduler_helper import scheduler
from common.utils.file_helper import delete_dir
import os
from database import SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):

    path = f"{os.getcwd()}/logs"

    remove_log_job_id = "clear_logs_job"
    remove_log_job = scheduler.get_job(job_id=remove_log_job_id)

    if remove_log_job is None: 
        scheduler.add_job(delete_dir, 'cron', day_of_week='fri', 
                      hour=0, minute=0, 
                      args=[path],
                      start_date=datetime.datetime.today(),
                      id="clear_logs_job")
    
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
