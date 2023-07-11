from business_rules.redis.connection import redis as rd
from ast import literal_eval
from common.const import ALERT_CONFIG, ALERT_STATUS

async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG)
        config_dict = literal_eval(config.decode('utf-8'))
        return config_dict
    except Exception as ex:
        print("((((((((((((((((((((ex))))))))))))))))))))")

def GetAlertStatus():
    status = rd.get(ALERT_STATUS)
    return status