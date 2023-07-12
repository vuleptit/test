from business_rules.redis.connection import redis as rd
from ast import literal_eval
from common.const import ALERT_CONFIG, ALERT_STATUS
from fastapi import HTTPException

async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG)
        config_dict = literal_eval(config.decode('utf-8'))
        return config_dict
    except Exception as ex:
        raise HTTPException(detail="Something went wrong", status_code=400) 

def GetAlertStatus():
    status = rd.get(ALERT_STATUS)
    return status