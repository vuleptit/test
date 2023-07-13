import logging
from fastapi import APIRouter, HTTPException, Response
from business_rules.redis.connection import redis as rd
# from common.const import AlertStatusObject
from business_rules.alert.alert_service import ProcessAlertOne, ProcessAlertTwo, GetCurentStatus, GetAlertConfig, SetAlertInitStatus
from common.const import AlertStatus
# from business_rules.alert.alert_service import test_redis
import logging
from common.utils.scheduler_helper import triggerhttp, scheduler, remove_status_obj
from datetime import datetime
from common.utils.random_helper import rand_id

logger = logging.getLogger('middleware')

router = APIRouter()

@router.get('/')
async def get_set_redis():
    try:
        random_id = rand_id()
        camid = random_id
        scheduler.add_job(triggerhttp, 'interval', seconds=4, id=random_id, args=[(random_id, camid)])
        config = await GetAlertConfig()
        return config
    except Exception as ex:
        print(ex)
        raise HTTPException(detail="get_set_redis route not work", status_code=400) 

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
        raise HTTPException("Something went wrong")


@router.get('/receive-alert-1')
async def receive_alert_one():
    # try:
        random_id = rand_id()
        camid = random_id
        status = await SetAlertInitStatus(id=camid)
        # should use camid
        status = await GetCurentStatus(id=camid)
        
        # scheduler.add_job(triggerhttp, 'interval', seconds=2, id=random_id, args=[(random_id, camid)], next_run_time=datetime.now()) # next_run_time=datetime.now()
        
        # job to remove object
        scheduler.add_job(remove_status_obj, 'interval', seconds=2, id=random_id, args=[(random_id, camid)])

        config = await GetAlertConfig()
        
        result = await ProcessAlertOne(config=config, alert_status=status, id=random_id)
        return result
    # except Exception as ex:
        
    #     raise HTTPException(status_code=400, detail="receive_alert_one not work")

@router.get('/receive-alert-2')
async def receive_alert_two():
    try:
        result = await ProcessAlertTwo()
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_two not work")


@router.get('/test-service-function')
async def test():
    result = await GetCurentStatus()
    return result

# @router.get('/test')
# async def test():
#     result = await test_redis()
#     return result