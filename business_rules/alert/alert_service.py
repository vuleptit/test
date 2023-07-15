from business_rules.redis.connection import redis as rd
from common.const import (ALERT_CONFIG_OBJ, AlertStatus, AlertName, 
                          COOLING_PERIOD_OBJ, COOLING_PERIOD_TIME, 
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
        logger.debug(f'Exception from GetCoolingPeriod: {str(ex)}')
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
        logger.debug(f"Cooling period: {cooling_per}, type: {type(cooling_per)}")

        start, time = cooling_per
        end_cooling = GetTimeAfterSecond(start=start, interval=int(time))
        return end_cooling <= datetime.datetime.now()
    except Exception as ex:
        logger.debug(f"Exception from IsFreeFromCoolingPeriod method: {str(ex)}")
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


# Alerts processing
async def ProcessAlertOne(alert_status, config, id):
    try:
        if alert_status == AlertStatus.OPEN_1.value:
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_1.value)
            
            # Scheduler job to trigger http
            trigger_job_random_id = f'alert1_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_1, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_1, AlertName.ALERT1)], 
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
        logger.debug(f'Exception from ProcessAlertOne: ' + str(ex))
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertTwo(alert_status, config, id):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)
        logger.debug(f"Is free from cooling period : {is_not_cooling}")
        current_status = await GetCurrentStatus(id=id)
        logger.debug(f"BEGIN PROCESS 2: Status id: {id} - Current status {current_status}")
        # if CLOSE_MODE_2 == "close":
        #     return "Alert 2 is in close mode" # Not used yet

        if IS_DISABLED_2:
            logger.debug(f'The process is rejected because the alert 2 is disabled')
            return "Alert 2 is now disabled"

        if alert_status == AlertStatus.OPEN_2.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 2"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_2.value)
            
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert2_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_2, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_2, AlertName.ALERT2)], 
                              next_run_time=datetime.datetime.now()) 
        
            return "The Alert two starts the processing successfully!"
        else:
            return HTTPException(detail="Alert two not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.debug(f'Exception from ProcessAlertTwo: ' + str(ex))
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)

async def ProcessAlertThree(alert_status, config, id):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)
        logger.debug(f"Is free from cooling period : {is_not_cooling}")
        current_status = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        logger.debug(f"BEGIN PROCESS 3: Status id: {id} - Current status {current_status}")
        
        # if CLOSE_MODE_3 == "close":
        #     return "Alert 3 is in close mode" # Not used yet

        if IS_DISABLED_3:
            logger.debug(f'The process is rejected because the alert 3 is disabled')
            return "Alert 3 is now disabled"
        
        if alert_status == AlertStatus.OPEN_3.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 3"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_3.value)
            
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert3_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_3, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_3, AlertName.ALERT3)], 
                              next_run_time=datetime.datetime.now())
            
            return "The Alert three starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 3 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.debug(f'Exception from ProcessAlertThree: ' + str(ex))
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFour(alert_status, config, id):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)
        logger.debug(f"Is free from cooling period : {is_not_cooling}")
        current_status = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        logger.debug(f"BEGIN PROCESS 4: Status id: {id} - Current status {current_status}")
        
        # if CLOSE_MODE_4 == "close":
        #     return "Alert 4 is in close mode" # Not used yet
        
        if alert_status == AlertStatus.OPEN_4.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 4"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_4.value)
            
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert4_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_4, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_4, AlertName.ALERT4)], 
                              next_run_time=datetime.datetime.now())

            return "The Alert four starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 4 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.debug(f'Exception from ProcessAlertFour: ' + str(ex))
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFive(alert_status, config, id):
    try:
        is_not_cooling = await IsFreeFromCoolingPeriod(id)
        logger.debug(f"Is free from cooling period : {is_not_cooling}")
        current_status = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        logger.debug(f"BEGIN PROCESS 5: Status id: {id} - Current status {current_status}")
        
        # if CLOSE_MODE_5 == "close":
        #     return "Alert 5 is in close mode" # Not used yet
        
        if alert_status == AlertStatus.OPEN_5.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 5"
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_5.value)
            
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert5_http_job_{id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_5, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_5, AlertName.ALERT5)], 
                              next_run_time=datetime.datetime.now())
    
            return "The Alert five starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 5 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.debug(f'Exception from ProcessAlertFive: ' + str(ex))
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    