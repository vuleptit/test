from fastapi import APIRouter, HTTPException, Request
from business_rules.alert.alert_service import GetAlertConfig, GetAlertStatus
import logging
from common.utils.scheduler_helper import myfunc, scheduler
from datetime import datetime
from common.utils.random_helper import rand_id

logger = logging.getLogger('middleware')

router = APIRouter()

@router.get('/')
async def get_set_redis():
    try:
        random_id = rand_id()
        scheduler.add_job(myfunc, 'interval', seconds=2, id=random_id, args=[random_id], next_run_time=datetime.now())
        config = await GetAlertConfig()
        return config
    except Exception as ex:
        print(ex)
        raise HTTPException(detail="Something went wrong", status_code=400) 
    
@router.get('/endpoint')
async def get_endpoint():
    try:
        data = data
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400) 
    
@router.post('/endpoint/')
async def post_endpoint():
    try:
        data = data
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400) 