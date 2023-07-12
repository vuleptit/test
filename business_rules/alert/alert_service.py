from business_rules.redis.connection import redis as rd
from ast import literal_eval
# from common.const import ALERT_CONFIG, ALERT_STATUS, AlertStatus
from fastapi import HTTPException

async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG)
        config_dict = literal_eval(config.decode('utf-8'))
        return config_dict
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400)

async def GetAlertStatus():
    try:
        alert_status = await rd.get(ALERT_STATUS)
        return alert_status
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400)

def SetAlertStatus(status):
    if not isinstance(status, AlertStatus):
        raise TypeError('status must be type AlertStatus')
    
def ProcessAlert(status):
    if not isinstance(status, AlertStatus):
        raise TypeError('status must be type AlertStatus')

    