from business_rules.redis.connection import redis as rd
from ast import literal_eval
from common.const import ALERT_CONFIG_OBJ, AlertStatus, AlertName, COOLING_PERIOD_OBJ, COOLING_PERIOD, CURRENT_STATUS
from fastapi import HTTPException
from fastapi import status
from common.utils.datetime_helper import GetCurrentTime, GetTimeAfterInterval
import pickle
import datetime

async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG_OBJ)
        config_dict = literal_eval(config.decode('utf-8'))
        return config_dict
    except Exception as ex:
        raise HTTPException(detail="GetAlertConfig() not work", status_code=400)

async def SetAlertInitStatus():
    try:
        result = await rd.set(CURRENT_STATUS, AlertStatus.OPEN_1.value)
        return result
    except Exception as ex:
        raise HTTPException(detail="SetAlertInitStatus() not work", status_code=400)

async def GetCurentStatus():
    try:
        alert_status = await rd.get(CURRENT_STATUS)
        return alert_status
    except Exception as ex:
        raise HTTPException(detail="GetCurentStatus() not work", status_code=400)
    
async def SetCoolingPeriod():
    cooling_obj = pickle.dumps([GetCurrentTime(), COOLING_PERIOD])
    result = await rd.set(COOLING_PERIOD_OBJ, cooling_obj)
    return result

async def ProcessReady():
    try:
        cooling_per = await rd.get(COOLING_PERIOD_OBJ)
        start, time = pickle.loads(cooling_per)
        end_cooling = GetTimeAfterInterval(start=start, time=time)
        return end_cooling <= datetime.datetime.now()
    except Exception as ex:
        raise HTTPException(detail="Process Ready is not working", status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertOne(alert_status):
    try:
        if alert_status == AlertStatus.OPEN_1.value:
            # Do something instead of pass 
            pass
            # Set status when done
            await rd.set(CURRENT_STATUS, AlertStatus.OPEN_2.value)
        else:
            return
        
    except Exception as ex:
        raise HTTPException(detail="ProcessAlertOne() not work", status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertTwo(alert_status):
    try:
        ready = ProcessReady()
        if alert_status == AlertStatus.OPEN_2.value and ready is True:
            # First thing to do
            await rd.set(CURRENT_STATUS, AlertStatus.PROCESSING_2)
            # Do something instead of pass
            
            # Need to change the state of alert
            await rd.set(CURRENT_STATUS, AlertStatus.OPEN_2.value)
            pass
        else:
            return
    except Exception as ex:
        raise HTTPException(detail="Cannot process alert one", status_code=status.HTTP_400_BAD_REQUEST)
    
async def test_redis():
    try:
        time = pickle.dumps([datetime.datetime.now(), 90])
        await rd.set("time", time)
        array = pickle.dumps([1,2])
        await rd.set("array", array)
        dict = pickle.dumps({'a':1})
        await rd.set("dict", dict)
        array = await rd.get("array")
        array = pickle.loads(array)
        dict = await rd.get("dict")
        dict = pickle.loads(dict)
        time = await rd.get("time")
        time = pickle.loads(time)
        test = await rd.get("shit")
        print(type(test))
        print(test)
        print(array)
        print(dict)
        print(time[0])
        print(type(time[0]))
        return
    except Exception as ex:
        print(ex)
        raise HTTPException(detail="smth", status_code=status.HTTP_400_BAD_REQUEST)
    
        

    

# async def GetAlertStatus(alertname: AlertStatusObject):
#     try:
#         alert_status = await rd.get(alertname)
#         return alert_status
#     except Exception as ex:
#         print(ex)
#         raise HTTPException(detail="Something went wrong", status_code=400)
    
