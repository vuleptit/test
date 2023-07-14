from fastapi import HTTPException
from common.const import LIMITED_TRIGGER_1
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import sleep
from common.utils.http_helper import http_post_endpoint, http_get_endpoint
from business_rules.redis.connection import redis as rd
from common.const import CURRENT_STATUS, LIMITED_TRIGGER_1, StatusField, ENDPOINT_URL, AlertStatus, COOLING_PERIOD, \
                            CLOSEMODE_2, CLOSEMODE_3, CLOSEMODE_4, CLOSEMODE_5
import logging
import pickle
from common.utils.datetime_helper import GetCurrentTime

logger = logging.getLogger('middleware')

scheduler = AsyncIOScheduler()
scheduler.start()

async def SetCoolingPeriod(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        logger.debug(f"COOLING_PERIOD: {COOLING_PERIOD}")
        cooling_obj = pickle.dumps([GetCurrentTime(), COOLING_PERIOD])
        result = await rd.hset(current_status_obj, StatusField.COOLING.value, cooling_obj)
        logger.debug(f"SetCoolingPeriod result: {result}")
        return result
    except Exception as ex:
        return "SetCoolingPeriod() not work"

async def GetNextStatus(current):
    if int(current) == 1:
        close_mode = [CLOSEMODE_2, CLOSEMODE_3, CLOSEMODE_4, CLOSEMODE_5]
        status = [AlertStatus.OPEN_2.value, AlertStatus.OPEN_3.value, AlertStatus.OPEN_4.value, AlertStatus.OPEN_5.value]
        next_status = [i for i in range(len(close_mode)) if close_mode[i] == "open"]
        if next_status: 
            next_status = next_status[0]
            return status[next_status]
        # all next are close
        else: 
            return await RemoveStatusObject()
    if int(current) == 2:
        close_mode = [CLOSEMODE_3, CLOSEMODE_4, CLOSEMODE_5]
        status = [AlertStatus.OPEN_3.value, AlertStatus.OPEN_4.value, AlertStatus.OPEN_5.value]
        next_status = [i for i in range(len(close_mode)) if close_mode[i] == "open"]
        if next_status: 
            next_status = next_status[0]
            return status[next_status]
        # all next are close
        else: 
            return await RemoveStatusObject()
    if int(current) == 3:
        close_mode = [CLOSEMODE_4, CLOSEMODE_5]
        status = [AlertStatus.OPEN_4.value, AlertStatus.OPEN_5.value]
        next_status = [i for i in range(len(close_mode)) if close_mode[i] == "open"]
        if next_status: 
            next_status = next_status[0]
            return status[next_status]
        # all next are close
        else: 
            return await RemoveStatusObject()
    if int(current) == 4:
        close_mode = [CLOSEMODE_5]
        status = [AlertStatus.OPEN_5.value]
        next_status = [i for i in range(len(close_mode)) if close_mode[i] == "open"]
        if next_status: 
            next_status = next_status[0]
            return status[next_status]
        # all next are close
        else: 
            return await RemoveStatusObject()

async def RemoveStatusObject(id, job_id):
    await rd.delete(CURRENT_STATUS + str(id))
    logger.debug("Done job 5")
    scheduler.remove_job(job_id=job_id)
    
async def TriggerHTTP(data):
    try:
        jobid, camid, limited, alert_num = data
        
        cur = await rd.hget(CURRENT_STATUS + str(camid), StatusField.STATUS.value)
        logger.debug(f"BEGIN TRIGGER HTTP: Status id: {camid} - Current status {cur}")
        # logger.debug(jobid, camid, limited, alert_num)
        # time of execution must not last longer than the job interval
        # http_post_endpoint(url=url, payload=data)
        current_status_obj = str(CURRENT_STATUS + str(camid))
        current_trigger_time = await rd.hget(current_status_obj, StatusField.TRIGGER_TIME.value)
        # action
        res = http_get_endpoint(ENDPOINT_URL)
        # --------------------------------
        if res.status_code == 400:
            # UPDATE TRIGGER TIME
            update_trigger_time = int(current_trigger_time) + 1
            await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, update_trigger_time)
            print("ok")
        else:
            print("not ok")
        
        if update_trigger_time >= limited:
            if int(alert_num) == 1:
                logger.debug("------------------")
                # await SetCoolingPeriod(id=camid)
                logger.debug("------------------")
                # next_status = AlertStatus.OPEN_2.value
                next_status = await GetNextStatus(1)
            elif int(alert_num) == 2:
                next_status = await GetNextStatus(2)
            elif int(alert_num) == 3:
                next_status = await GetNextStatus(3)
            elif int(alert_num) == 4:
                next_status = await GetNextStatus(4)
            elif int(alert_num) == 5:
                # Delete object when done job 5
                await RemoveStatusObject(id=camid, job_id=jobid)
                scheduler.remove_job(job_id=jobid)
                return
            
            # Update STATUS
            await rd.hset(CURRENT_STATUS + str(camid), StatusField.STATUS.value, next_status)
            await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, 0)
            scheduler.remove_job(job_id=jobid)

        cur = await rd.hget(CURRENT_STATUS + str(camid), StatusField.STATUS.value)
        logger.debug(f"END TRIGGER HTTP trigger time: {update_trigger_time} - Status id: {camid} - Current status {cur}")
        return
    except Exception as ex:
        raise HTTPException(detail="TriggerHTTP not work", status_code=400)
        

async def remove_status_obj(data):
    camid = data
    current_status_obj = str(CURRENT_STATUS + str(camid))
    return await rd.delete(current_status_obj) 

    
    