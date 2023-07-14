from fastapi import HTTPException
from common.const import LIMITED_TRIGGER_1
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import sleep
from common.utils.http_helper import http_post_endpoint, http_get_endpoint
from business_rules.redis.connection import redis as rd
from common.const import CURRENT_STATUS, LIMITED_TRIGGER_1, StatusField, ENDPOINT_URL, AlertStatus
import logging

logger = logging.getLogger('middleware')

scheduler = AsyncIOScheduler()
scheduler.start()


async def triggerhttp(data):
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
        
        if res.status_code == 200:
            update_trigger_time = int(current_trigger_time) + 1
            await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, update_trigger_time)
            print("ok")
        
        if update_trigger_time >= limited:
            if int(alert_num) == 1:
                next_status = AlertStatus.OPEN_2.value
            elif int(alert_num) == 2:
                next_status = AlertStatus.OPEN_3.value
            elif int(alert_num) == 3:
                next_status = AlertStatus.OPEN_4.value
            elif int(alert_num) == 4:
                next_status = AlertStatus.OPEN_5.value
            elif int(alert_num) == 5:
                next_status = AlertStatus.OPEN_1.value
                # Delete object when done job 5
                await rd.delete(CURRENT_STATUS + str(id))
                scheduler.remove_job(job_id=jobid)
                
            await rd.hset(CURRENT_STATUS + str(camid), StatusField.STATUS.value, next_status)
            await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, 0)
            scheduler.remove_job(job_id=jobid)

        cur = await rd.hget(CURRENT_STATUS + str(camid), StatusField.STATUS.value)
        logger.debug(f"END TRIGGER HTTP trigger time: {update_trigger_time} - Status id: {camid} - Current status {cur}")
            
    except Exception as ex:
        raise HTTPException(detail="triggerhttp not work", status_code=400)
        


async def remove_status_obj(data):
    camid = data
    current_status_obj = str(CURRENT_STATUS + str(camid))
    return await rd.delete(current_status_obj) 

    
    