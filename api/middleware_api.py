import logging
from fastapi import APIRouter, HTTPException, Response
from business_rules.alert.alert_service import ProcessAlertOne, ProcessAlertTwo, GetCurentStatus, GetAlertConfig, \
                                                SetAlertInitStatus, ProcessAlertThree, \
                                                ProcessAlertFour, ProcessAlertFive 
from fastapi import status as st
import logging
from business_rules.redis.connection import redis as rd

logger = logging.getLogger('middleware')

router = APIRouter()

@router.get("/receive-alert-1/{camid}")
async def receive_alert_one(camid):
    try:
        # handleid
        
        status = await GetCurentStatus(id=camid)
        if status is not None:
            return HTTPException(detail="Alert one not open, other still processing", status_code=st.HTTP_400_BAD_REQUEST)
        
        await SetAlertInitStatus(id=camid)
        
        status = await GetCurentStatus(id=camid)
        config = await GetAlertConfig()
        result = await ProcessAlertOne(config=config, alert_status=status, id=camid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_one not work")

@router.get("/receive-alert-2/{camid}")
async def receive_alert_two(camid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=camid)
        config = await GetAlertConfig()
        result = await ProcessAlertTwo(alert_status=status, config=config, id=camid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_two not work")

@router.get("/receive-alert-3/{camid}")
async def receive_alert_three(camid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=camid)
        config = await GetAlertConfig()
        result = await ProcessAlertThree(alert_status=status, config=config, id=camid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_3 not work")

@router.get("/receive-alert-4/{camid}")
async def receive_alert_four(camid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=camid)
        config = await GetAlertConfig()
        result = await ProcessAlertFour(alert_status=status, config=config, id=camid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_4 not work")

@router.get("/receive-alert-5/{camid}")
async def receive_alert_five(camid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=camid)
        config = await GetAlertConfig()
        result = await ProcessAlertFive(alert_status=status, config=config, id=camid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_5 not work")

# @router.get("/test-service-function/{id}")
# async def test(id):
#     result = await GetCurentStatus(id)
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