import logging
import requests as rq
from fastapi import APIRouter, HTTPException, Response, Request
from business_rules.alert.alert_service import (ProcessAlertOne, ProcessAlertTwo, 
                                                GetCurrentStatus, GetAlertConfig, 
                                                SetAlertInitStatus, ProcessAlertThree, 
                                                ProcessAlertFour, ProcessAlertFive)
from fastapi import status as st
import logging
from business_rules.redis.connection import redis as rd

logger = logging.getLogger('middleware')

router = APIRouter()

@router.get("/receive-alert-1/{cam_id}")
async def receive_alert_one(request: Request, cam_id):
    try:
        url_params = request.query_params._dict
        current_status = await GetCurrentStatus(id=cam_id)
        if current_status is not None:
            return HTTPException(detail="Another process is running", 
                                 status_code=st.HTTP_400_BAD_REQUEST)
        
        # Init the object for the new process
        await SetAlertInitStatus(id=cam_id)
        
        # Process the Alert 1
        current_status = await GetCurrentStatus(id=cam_id)
        config = await GetAlertConfig()
        result = await ProcessAlertOne(config=config, alert_status=current_status, id=cam_id, params=url_params)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_one not work")

@router.get("/receive-alert-2/{cam_id}")
async def receive_alert_two(request: Request, cam_id):
    try:
        # handleid
        
        #
        url_params = request.query_params._dict
        status = await GetCurrentStatus(id=cam_id)
        config = await GetAlertConfig()
        result = await ProcessAlertTwo(alert_status=status, config=config, id=cam_id, params=url_params)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_two not work")

@router.get("/receive-alert-3/{cam_id}")
async def receive_alert_three(request: Request, cam_id):
    try:
        # handleid
        
        #
        url_params = request.query_params._dict
        status = await GetCurrentStatus(id=cam_id)
        config = await GetAlertConfig()
        result = await ProcessAlertThree(alert_status=status, config=config, id=cam_id, params=url_params)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_3 not work")

@router.get("/receive-alert-4/{cam_id}")
async def receive_alert_four(request: Request, cam_id):
    try:
        # handleid
        
        #
        url_params = request.query_params._dict
        status = await GetCurrentStatus(id=cam_id)
        config = await GetAlertConfig()
        result = await ProcessAlertFour(alert_status=status, config=config, id=cam_id, params=url_params)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_4 not work")

@router.get("/receive-alert-5/{cam_id}")
async def receive_alert_five(request: Request, cam_id):
    try:
        # handleid
        
        #
        url_params = request.query_params._dict
        status = await GetCurrentStatus(id=cam_id)
        config = await GetAlertConfig()
        result = await ProcessAlertFive(alert_status=status, config=config, id=cam_id, params=url_params)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_5 not work")

# @router.get("/test-service-function/{id}")
# async def test(id):
#     result = await GetCurrentStatus(id)
#     # result = await rd.ttl("alert_status_current1")
#     return result

# @router.get('/test')
# async def test():
#     # result = await test_redis()
#     result = await rd.delete("alert_status_current25")
#     return result

@router.get('/free')
def free():
    return Response(content='a', status_code=200)