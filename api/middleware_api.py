import logging
from fastapi import APIRouter, HTTPException
from business_rules.alert.alert_service import ProcessAlertOne, ProcessAlertTwo, GetCurentStatus, GetAlertConfig, \
                                                SetAlertInitStatus, ProcessAlertThree, \
                                                ProcessAlertFour, ProcessAlertFive
import logging

logger = logging.getLogger('middleware')

router = APIRouter()

@router.get("/receive-alert-1/{testid}")
async def receive_alert_one(testid):
    try:
        # handleid
        
        #
        await SetAlertInitStatus(id=testid)
        status = await GetCurentStatus(id=testid)
        logger.debug(f"Status id: {testid} - Current status {status}")
        config = await GetAlertConfig()
        result = await ProcessAlertOne(config=config, alert_status=status, id=testid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_one not work")

@router.get("/receive-alert-2/{testid}")
async def receive_alert_two(testid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=testid)
        config = await GetAlertConfig()
        result = await ProcessAlertTwo(alert_status=status, config=config, id=testid)
        return result
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail="receive_alert_two not work")

@router.get("/receive-alert-3/{testid}")
async def receive_alert_three(testid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=testid)
        config = await GetAlertConfig()
        result = await ProcessAlertThree(alert_status=status, config=config, id=testid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_3 not work")

@router.get("/receive-alert-4/{testid}")
async def receive_alert_four(testid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=testid)
        config = await GetAlertConfig()
        result = await ProcessAlertFour(alert_status=status, config=config, id=testid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_4 not work")

@router.get("/receive-alert-5/{testid}")
async def receive_alert_five(testid):
    try:
        # handleid
        
        #
        status = await GetCurentStatus(id=testid)
        config = await GetAlertConfig()
        result = await ProcessAlertFive(alert_status=status, config=config, id=testid)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_5 not work")


@router.get("/test-service-function")
async def test():
    result = await GetCurentStatus()
    return result

# @router.get('/test')
# async def test():
#     result = await test_redis()
#     return result