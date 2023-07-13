from business_rules.redis.connection import redis as rd
from ast import literal_eval
from common.const import ALERT_CONFIG_OBJ, AlertStatus, AlertName, COOLING_PERIOD_OBJ, COOLING_PERIOD, CURRENT_STATUS, StatusField
from fastapi import HTTPException
from fastapi import status
from common.utils.datetime_helper import GetCurrentTime, GetTimeAfterInterval
import pickle
import datetime

async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG_OBJ)
        config = pickle.loads(config)
        return config
    except Exception as ex:
        raise HTTPException(detail="GetAlertConfig() not work", status_code=400)

async def SetAlertInitStatus(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        await rd.hset(current_status_obj, StatusField.STATUS.value, AlertStatus.OPEN_1.value)
        await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, 0)
        init_cooling_value = pickle.dumps([GetCurrentTime(), 0])
        await rd.hset(current_status_obj, StatusField.COOLING.value, init_cooling_value)
    except Exception as ex:
        print(ex)
        raise HTTPException(detail="SetAlertInitStatus() not work", status_code=400)

async def GetCurentStatus(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        alert_status = await rd.hget(current_status_obj, StatusField.STATUS.value)
        return alert_status
    except Exception as ex:
        raise HTTPException(detail="GetCurentStatus() not work", status_code=400)
    
async def SetCoolingPeriod():
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        cooling_obj = pickle.dumps([GetCurrentTime(), COOLING_PERIOD])
        result = await rd.hset(current_status_obj, StatusField.COOLING, cooling_obj)
        return result
    except Exception as ex:
        raise HTTPException(detail="SetCoolingPeriod() not work", status_code=400)
    
async def GetCoolingPeriod():
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        result = await rd.hget(current_status_obj, StatusField.COOLING)
        cooling_obj = pickle.loads(result)
        return cooling_obj
    except Exception as ex:
        raise HTTPException(detail="GetCoolingPeriod() not work", status_code=400)

async def ProcessReady():
    try:
        cooling_per = await rd.get(COOLING_PERIOD_OBJ)
        if cooling_per is None:
            return True
        else:
            start, time = GetCoolingPeriod()
            end_cooling = GetTimeAfterInterval(start=start, time=time)
            return end_cooling <= datetime.datetime.now()
    except Exception as ex:
        raise HTTPException(detail="ProcessReady() not working", status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertOne(alert_status, config, id):
    try:
        print(alert_status)
        if alert_status == AlertStatus.OPEN_1.value:
            # Do something instead of pass
            
            # Set status when done
            await rd.hset(CURRENT_STATUS, StatusField.STATUS, AlertStatus.OPEN_2.value)
            return True
        else:
            return HTTPException(detail="Alert one not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        print(ex)
        raise HTTPException(detail="ProcessAlertOne() not work", status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertTwo(alert_status, id=None):
    try:
        ready = ProcessReady()
        
        if alert_status == AlertStatus.OPEN_2.value and ready is True:
            # First thing to do
            await rd.set(CURRENT_STATUS, AlertStatus.PROCESSING_2)
            # await rd.hset(CURRENT_STATUS, id, AlertStatus.PROCESSING_2)
            # Do something instead of pass
            
            # Need to change the state of alert
            await rd.set(CURRENT_STATUS, AlertStatus.OPEN_2.value)
            pass
        else:
            raise HTTPException(detail="Alert two not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        raise HTTPException(detail="Cannot process alert one", status_code=status.HTTP_400_BAD_REQUEST)


# async def GetAlertStatus(alertname: AlertStatusObject):
#     try:
#         alert_status = await rd.get(alertname)
#         return alert_status
#     except Exception as ex:
#         print(ex)
#         raise HTTPException(detail="Something went wrong", status_code=400)
    

# async def test_redis():
#     try:
#         time = pickle.dumps([datetime.datetime.now(), 90])
#         await rd.set("time", time)
#         array = pickle.dumps([1,2])
#         await rd.set("array", array)
#         dict = pickle.dumps({'a':1})
#         await rd.set("dict", dict)
#         array = await rd.get("array")
#         array = pickle.loads(array)
#         dict = await rd.get("dict")
#         dict = pickle.loads(dict)
#         time = await rd.get("time")
#         time = pickle.loads(time)
#         test = await rd.get("shit")
#         print(type(test))
#         print(test)
#         print(array)
#         print(dict)
#         print(time[0])
#         print(type(time[0]))
#         return
#     except Exception as ex:
#         print(ex)
#         raise HTTPException(detail="smth", status_code=status.HTTP_400_BAD_REQUEST)