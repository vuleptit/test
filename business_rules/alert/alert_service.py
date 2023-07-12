from business_rules.redis.connection import redis as rd
from ast import literal_eval
from common.const import ALERT_CONFIG, ALERT_STATUS, AlertStatus, AlertName
from fastapi import HTTPException
from fastapi import status
import requests

async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG)
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

async def GetAlertStatus():
    try:
        alert_status = await rd.get(ALERT_STATUS)
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
        await rd.set(ALERT_STATUS, AlertStatus.OPEN_fOR_ALERT_2.value)
    except Exception as ex:
        raise HTTPException(detail="Cannot process alert one", status_code=status.HTTP_400_BAD_REQUEST)

        

    

    