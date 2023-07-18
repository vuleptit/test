from business_rules.redis.connection import redis as rd
from common.const import (ALERT_CONFIG_OBJ, AlertStatus, AlertName, 
                          COOLING_PERIOD_OBJ, COOLING_PERIOD_TIME, MAX_EXECUTION_TIME,
                          CURRENT_STATUS, StatusField, TIME_TO_RESET_CYCLE, 
                          INTERVAL_1, INTERVAL_2, INTERVAL_3, INTERVAL_4, INTERVAL_5, 
                          LIMITED_TRIGGER_1, LIMITED_TRIGGER_2, LIMITED_TRIGGER_3, 
                          LIMITED_TRIGGER_4, LIMITED_TRIGGER_5, CLOSE_MODE_2, 
                          CLOSE_MODE_3, CLOSE_MODE_4, CLOSE_MODE_5, DEFAULT_EXCEPTION_MESSAGE,
                          IS_DISABLED_1, IS_DISABLED_2, IS_DISABLED_3, IS_DISABLED_4, IS_DISABLED_5)
from fastapi import HTTPException
from fastapi import status
from common.utils.datetime_helper import GetCurrentTime, GetTimeAfterSecond
from common.utils.random_helper import rand_id
from common.utils.scheduler_helper import TriggerHTTP, scheduler, remove_status_obj
from business_rules.logging.logging_service import write_log
import logging
import pickle
import datetime

logger = logging.getLogger('middleware')

# Configurations
async def GetAlertConfig():
    try:
        config = await rd.get(ALERT_CONFIG_OBJ)
        config = pickle.loads(config)
        return config
    except Exception as ex:
        return HTTPException(detail="GetAlertConfig() not work", status_code=400)

async def SetAlertInitStatus(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        await rd.hset(current_status_obj, StatusField.STATUS.value, AlertStatus.OPEN_1.value)
        await rd.hset(current_status_obj, StatusField.TRIGGER_TIME.value, 0)

        init_cooling_value = pickle.dumps([GetCurrentTime(), 0])
        await rd.hset(current_status_obj, StatusField.COOLING.value, init_cooling_value)
        await rd.expire(current_status_obj, TIME_TO_RESET_CYCLE)
    except Exception as ex:
        return "SetAlertInitStatus() not work"
    
async def GetCoolingPeriod(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        result = await rd.hget(current_status_obj, StatusField.COOLING.value)
        if result is None or result == '':
            return None
        else:
            cooling_obj = pickle.loads(result)
            return cooling_obj
    except Exception as ex:
        write_log(log_str=f'Exception from GetCoolingPeriod: {str(ex)}', camera_id=id)
        return DEFAULT_EXCEPTION_MESSAGE

# Check the readiness of the Process for the Alert
async def IsFreeFromCoolingPeriod(id):
    try:
        # If the process is in Cooling period
        #   If the cooling time is not over, return exception
        #   If the cooling time is over,
        #       check if the processing can turn into the "process" status of the Alert
        cooling_per = await GetCoolingPeriod(id=id)

        if cooling_per is None:
            return True

        start, time = cooling_per
        end_cooling = GetTimeAfterSecond(start=start, interval=int(time))

        is_cooling_period_free = end_cooling <= datetime.datetime.now()

        write_log(log_str=f"Checking cooling period"
                          + f"\nStart time: {start.strftime('%d/%m/%y %H:%M:%s')}"
                          + f"\nEnd time: {end_cooling.strftime('%d/%m/%y %H:%M:%s')}"
                          + f"\nIs still in Cooling time: {is_cooling_period_free == False}", camera_id=id)

        return is_cooling_period_free
    except Exception as ex:
        write_log(log_str=f"Exception from IsFreeFromCoolingPeriod method: {str(ex)}", camera_id=id)
        return DEFAULT_EXCEPTION_MESSAGE

async def GetCurrentStatus(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        alert_status = await rd.hget(current_status_obj, StatusField.STATUS.value)
        if alert_status is None:
            return alert_status
        # Decode byte value to string
        alert_status = alert_status.decode("utf-8")
        return alert_status
    except Exception as ex:
        return "GetCurrentStatus() not work"
    
# Keep the job alive until done
async def KeepJobAlive(interval, limited, status_object):
    job_time = interval * limited
    
    status_obj_ttl = await rd.ttl(status_object)
    if job_time >= status_obj_ttl:
        return await rd.expire(status_object, job_time + MAX_EXECUTION_TIME)

# Alerts processing
async def ProcessAlertOne(alert_status, config, id, params):
    try:
        if alert_status == AlertStatus.OPEN_1.value:
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_1.value)
            await KeepJobAlive(interval=INTERVAL_1, limited=LIMITED_TRIGGER_1, status_object=CURRENT_STATUS + str(id))
            # Scheduler job to trigger http
            trigger_job_random_id = f'alert1_http_job_{id}'
            
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_1,
                              id=trigger_job_random_id,
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_1, AlertName.ALERT1, params)],
                              next_run_time=datetime.datetime.now())
            
            # Scheduler job to auto-remove from redis
            scheduler.add_job(remove_status_obj, 'date', 
                              run_date=GetTimeAfterSecond(GetCurrentTime(), TIME_TO_RESET_CYCLE), 
                              args=[id])
            
            return "The Alert one starts the processing successfully!"
        else:
            return HTTPException(detail="The process is not opening for the Alert one", 
                                 status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertOne: {str(ex)}', camera_id=id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertTwo(alert_status, config, id, params):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)

        if is_not_cooling is False:
            return

        current_status = await GetCurrentStatus(id=id)
        write_log(log_str=f"BEGIN PROCESS 2:"
                          + f"\nCamera id: {id}"
                          + f"\nCurrent status: {current_status}", camera_id=id)
        # if CLOSE_MODE_2 == "close":
        #     return "Alert 2 is in close mode" # Not used yet

        if IS_DISABLED_2:
            write_log(log_str=f'The process is rejected because the alert 2 is disabled', camera_id=id)
            return "Alert 2 is now disabled"

        if alert_status == AlertStatus.OPEN_2.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 2"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_2.value)
            await KeepJobAlive(interval=INTERVAL_2, limited=LIMITED_TRIGGER_2, status_object=CURRENT_STATUS + str(id))
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert2_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_2, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_2, AlertName.ALERT2, params)],
                              next_run_time=datetime.datetime.now()) 
        
            return "The Alert two starts the processing successfully!"
        else:
            return HTTPException(detail="Alert two not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertTwo: {str(ex)}', camera_id=id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)

async def ProcessAlertThree(alert_status, config, id, params):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)

        if is_not_cooling is False:
            return

        current_status = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        write_log(log_str=f"BEGIN PROCESS 3:"
                          + f"\nCamera id: {id}"
                          + f"\nCurrent status: {current_status}", camera_id=id)
        
        # if CLOSE_MODE_3 == "close":
        #     return "Alert 3 is in close mode" # Not used yet

        if IS_DISABLED_3:
            write_log(log_str=f'The process is rejected because the alert 3 is disabled', camera_id=id)
            return "Alert 3 is now disabled"
        
        if alert_status == AlertStatus.OPEN_3.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 3"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_3.value)
            await KeepJobAlive(interval=INTERVAL_3, limited=LIMITED_TRIGGER_3, status_object=CURRENT_STATUS + str(id))
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert3_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_3, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_3, AlertName.ALERT3, params)],
                              next_run_time=datetime.datetime.now())
            
            return "The Alert three starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 3 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertThree: {str(ex)}', camera_id=id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFour(alert_status, config, id, params):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)

        if is_not_cooling is False:
            return

        current_status = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        write_log(log_str=f"BEGIN PROCESS 4:"
                          + f"\nCamera id: {id}"
                          + f"\nCurrent status: {current_status}", camera_id=id)
        
        # if CLOSE_MODE_4 == "close":
        #     return "Alert 4 is in close mode" # Not used yet
        
        if alert_status == AlertStatus.OPEN_4.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 4"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_4.value)
            await KeepJobAlive(interval=INTERVAL_4, limited=LIMITED_TRIGGER_4, status_object=CURRENT_STATUS + str(id))
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert4_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_4, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_4, AlertName.ALERT4, params)],
                              next_run_time=datetime.datetime.now())

            return "The Alert four starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 4 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertFour: {str(ex)}', camera_id=id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFive(alert_status, config, id, params):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)

        if is_not_cooling is False:
            return

        current_status = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        write_log(log_str=f"BEGIN PROCESS 5:"
                          + f"\nCamera id: {id}"
                          + f"\nCurrent status: {current_status}", camera_id=id)
        
        # if CLOSE_MODE_5 == "close":
        #     return "Alert 5 is in close mode" # Not used yet
        
        if alert_status == AlertStatus.OPEN_5.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 5"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_5.value)
            await KeepJobAlive(interval=INTERVAL_5, limited=LIMITED_TRIGGER_5, status_object=CURRENT_STATUS + str(id))
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert5_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_5,
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_5, AlertName.ALERT5, params)],
                              next_run_time=datetime.datetime.now())
    
            return "The Alert five starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 5 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertFive: {str(ex)}', camera_id=id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    