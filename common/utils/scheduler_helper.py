from fastapi import HTTPException
from common.const import LIMITED_TRIGGER_1
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import sleep
from common.utils.http_helper import http_post_endpoint, http_get_endpoint
from business_rules.redis.connection import redis as rd
from common.const import (CURRENT_STATUS, LIMITED_TRIGGER_1, StatusField, 
                          ENDPOINT_URL, AlertStatus, COOLING_PERIOD_TIME, 
                          IS_DISABLED_2, IS_DISABLED_3, IS_DISABLED_4, IS_DISABLED_5,
                          DEFAULT_EXCEPTION_MESSAGE, IS_COOLING_STATUS_ENABLED,
                          HTTP_STATUS_OK, AlertName)
from business_rules.logging.logging_service import write_log
import pickle
from common.utils.datetime_helper import GetCurrentTime

scheduler = AsyncIOScheduler()
scheduler.start()

async def SetCoolingPeriod(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        current_date_time = GetCurrentTime()
        cooling_obj = pickle.dumps([current_date_time, COOLING_PERIOD_TIME])
        result = await rd.hset(current_status_obj, StatusField.COOLING.value, cooling_obj)

        write_log(
            log_str=f"The cooling period for the camera {id} "
                    + f"has been set with the time: {current_date_time.strftime('%d/%m/%y %H:%M:%s')}"
                    + f"\nCooling period length: {COOLING_PERIOD_TIME} second(s)", 
            camera_id=id)
        
        return result
    except Exception as ex:
        write_log(log_str=f"Exception from SetCoolingPeriod method: {str(ex)}", camera_id=id)
        return DEFAULT_EXCEPTION_MESSAGE

async def GetNextStatus(alert_name, cam_id = '', job_id = ''):
    if alert_name == AlertName.ALERT1:
        lst_is_disabled = [IS_DISABLED_2, IS_DISABLED_3, IS_DISABLED_4, IS_DISABLED_5]
        lst_next_status = [AlertStatus.OPEN_2.value, AlertStatus.OPEN_3.value, 
                           AlertStatus.OPEN_4.value, AlertStatus.OPEN_5.value]
    elif alert_name == AlertName.ALERT2:
        lst_is_disabled = [IS_DISABLED_3, IS_DISABLED_4, IS_DISABLED_5]
        lst_next_status = [AlertStatus.OPEN_3.value, AlertStatus.OPEN_4.value, AlertStatus.OPEN_5.value]
    elif alert_name == AlertName.ALERT3:
        lst_is_disabled = [IS_DISABLED_4, IS_DISABLED_5]
        lst_next_status = [AlertStatus.OPEN_4.value, AlertStatus.OPEN_5.value]
    elif  alert_name == AlertName.ALERT4:
        lst_is_disabled = [IS_DISABLED_5]
        lst_next_status = [AlertStatus.OPEN_5.value]
        
    # Get the index of the first next ENABLED status 
    next_status_index = next(i for i,v in enumerate(lst_is_disabled) if v == False) \
                            if False in lst_is_disabled else None

    if next_status_index is not None: 
        return lst_next_status[next_status_index]
    else: 
        # If all other Alert is disabled -> All Alerts are done -> Remove object from Redis
        return await RemoveStatusObject(id=cam_id, job_id=job_id)
    
# Remove the object from redis
async def RemoveStatusObject(id, job_id):
    await rd.delete(CURRENT_STATUS + str(id))
    write_log(log_str=f"The data for the camera {id} has been removed.", camera_id=id)
    scheduler.remove_job(job_id=job_id)
    
async def TriggerHTTP(data):
    try:
        job_id, cam_id, limited, alert_name = data
        current_status_obj = str(CURRENT_STATUS + str(cam_id))
        current_trigger_time = await rd.hget(current_status_obj, StatusField.TRIGGER_TIME.value)

        cur = await rd.hget(CURRENT_STATUS + str(cam_id), StatusField.STATUS.value)
        write_log(log_str=f"""
BEGIN TRIGGER HTTP:
Job id: {job_id}
Camera id: {cam_id}
Current status: {str(cur)}
Limited call times: {limited}
Current call time: {str(current_trigger_time)}""", camera_id=cam_id)

        # Trigger http endpoint
        res = http_get_endpoint(ENDPOINT_URL)  

        write_log(log_str=f"""
Trigger http done for the camera {cam_id}
Endpoint: {ENDPOINT_URL}
Response: {str(res)}""", camera_id=cam_id)
        
        update_trigger_time = int(current_trigger_time) + 1
        current_trigger_time = await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, update_trigger_time)

        if update_trigger_time >= limited:
            if alert_name == AlertName.ALERT5:
                # Delete object when the Alert 5 process is done
                await RemoveStatusObject(id=cam_id, job_id=job_id)
                scheduler.remove_job(job_id=job_id)
                return    
            
            scheduler.remove_job(job_id=job_id)

            if alert_name == AlertName.ALERT1:
                if IS_COOLING_STATUS_ENABLED:
                    await SetCoolingPeriod(id=cam_id)

            next_status = await GetNextStatus(alert_name)
            
            # Update STATUS
            await rd.hset(CURRENT_STATUS + str(cam_id), StatusField.STATUS.value, next_status)
            # Reset trigger times of the scheduler job
            await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, 0)

        cur = await rd.hget(CURRENT_STATUS + str(cam_id), StatusField.STATUS.value)
        return
    except Exception as ex:
        write_log(log_str=f"Exception from TriggerHTTP: {str(ex)}", camera_id=cam_id)
        raise HTTPException(detail=f"TriggerHTTP not work with exception {str(ex)}", status_code=400)
        

async def remove_status_obj(data):
    cam_id = data
    current_status_obj = str(CURRENT_STATUS + str(cam_id))
    await rd.delete(current_status_obj) 
    write_log(log_str=f'Removed the object from redis. End the cycle of the camera {cam_id}', camera_id=cam_id)
