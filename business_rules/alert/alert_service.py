from business_rules.redis.connection import redis as rd
from ast import literal_eval
from common.const import ALERT_CONFIG_OBJ, AlertStatus, AlertName, COOLING_PERIOD_OBJ, COOLING_PERIOD, AlertStatusObject
from fastapi import HTTPException
from fastapi import status
from common.utils.datetime_helper import GetCurrentTime, GetTimeAfterInterval
import requests
import pickle
import datetime

async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG_OBJ)
        config_dict = literal_eval(config.decode('utf-8'))
        return config_dict
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400)

async def SetAlertStatus():
    try:
        result = await rd.set(AlertName.ALERT1.value, AlertStatus.OPEN_fOR_ALERT_1.value)
        return result
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400)

async def GetCurentStatus(alertname: AlertStatusObject):
    try:
        alert_status = await rd.get(AlertStatusObject)
        return alert_status
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400)
    
async def GetAlertStatus():
    try:
        alert_status = await rd.get(AlertStatusObject)
        return alert_status
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400)

async def ProcessAlertOne(alert_status, data):
    try:
        if alert_status == AlertStatus.OPEN_fOR_ALERT_1.value:
            # Do something instead of pass 
            pass
        else:
            return
        await rd.set(AlertStatusObject.ALERT1.value, AlertStatus.OPEN_fOR_ALERT_2.value)
    except Exception as ex:
        raise HTTPException(detail="Cannot process alert one", status_code=status.HTTP_400_BAD_REQUEST)

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
    
async def ProcessAlertTwo(alert_status, data):
    try:
        ready = ProcessReady()
        if alert_status == AlertStatus.OPEN_fOR_ALERT_2.value and ready is True:
            # First thing to do
            await rd.set(ALERT_STATUS_OBJ, AL)
            # Do something instead of pass
            
            # Need to change the state of alert
            await rd.set(ALERT_STATUS_OBJ, AlertStatus.OPEN_fOR_ALERT_2.value)
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
        print(array)
        print(dict)
        print(time[0])
        print(type(time[0]))
        return
    except Exception as ex:
        print(ex)
        raise HTTPException(detail="smth", status_code=status.HTTP_400_BAD_REQUEST)
    
        

    

    