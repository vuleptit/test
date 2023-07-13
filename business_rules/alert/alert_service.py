from business_rules.redis.connection import redis as rd
from common.const import ALERT_CONFIG_OBJ, AlertStatus, AlertName, COOLING_PERIOD_OBJ, COOLING_PERIOD, \
                        CURRENT_STATUS, StatusField, TIME_TO_RESET_CYCLE, \
                        INTERVAL_1, INTERVAL_2, INTERVAL_3, INTERVAL_4, INTERVAL_5, \
                        LIMITED_TRIGGER_1, LIMITED_TRIGGER_2, LIMITED_TRIGGER_3, LIMITED_TRIGGER_4, LIMITED_TRIGGER_5
from fastapi import HTTPException
from fastapi import status
from common.utils.datetime_helper import GetCurrentTime, GetTimeAfterSecond
from common.utils.random_helper import rand_id
from common.utils.scheduler_helper import triggerhttp, scheduler, remove_status_obj
import logging
import pickle
import datetime

logger = logging.getLogger('middleware')

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
        # init_cooling_value = pickle.dumps([GetCurrentTime(), 0])
        # await rd.hset(current_status_obj, StatusField.COOLING.value, init_cooling_value)
        await rd.hset(current_status_obj, StatusField.COOLING.value, "")
        await rd.expire(current_status_obj, TIME_TO_RESET_CYCLE)
    except Exception as ex:
        return "SetAlertInitStatus() not work"

async def SetCoolingPeriod(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        cooling_obj = pickle.dumps([GetCurrentTime(), COOLING_PERIOD])
        result = await rd.hset(current_status_obj, StatusField.COOLING.value, cooling_obj)
        return result
    except Exception as ex:
        return "SetCoolingPeriod() not work"
    
async def GetCoolingPeriod(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        result = await rd.hget(current_status_obj, StatusField.COOLING)
        cooling_obj = pickle.loads(result)
        return cooling_obj
    except Exception as ex:
        return "GetCoolingPeriod() not work"

async def ProcessReady(id):
    try:
        cooling_per = await rd.hget(CURRENT_STATUS + str(id), StatusField.COOLING)
        cooling_per = cooling_per.decode('utf-8')
        logger.debug(f"Cooling period: {cooling_per}, type: {type(cooling_per)}")
        if cooling_per is None or cooling_per == '':
            return True
        else:
            start, time = await GetCoolingPeriod(id=id)
            end_cooling = GetTimeAfterSecond(start=start, time=time)
            return end_cooling <= datetime.datetime.now()
    except Exception as ex:
        return "ProcessReady() not working"

async def GetCurentStatus(id):
    try:
        current_status_obj = CURRENT_STATUS + str(id)
        alert_status = await rd.hget(current_status_obj, StatusField.STATUS.value)
        # Decode byte value to string
        alert_status = alert_status.decode("utf-8")
        return alert_status
    except Exception as ex:
        return "GetCurentStatus() not work"
    
async def ProcessAlertOne(alert_status, config, id):
    try:
        if alert_status == AlertStatus.OPEN_1.value:
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_1.value)
            
            trigger_job_random_id = rand_id()
            # 1 is this alert name
            scheduler.add_job(triggerhttp, 'interval', seconds=3, id=trigger_job_random_id, args=[(trigger_job_random_id, id, LIMITED_TRIGGER_1, 1)]) # next_run_time=datetime.now()
            # job to remove object
            scheduler.add_job(remove_status_obj, 'date', run_date=GetTimeAfterSecond(GetCurrentTime(), TIME_TO_RESET_CYCLE), args=[id])
            # Set status when done
            return "done process alert one - maybe still triggering"
        else:
            return HTTPException(detail="Alert one not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        raise HTTPException(detail="ProcessAlertOne() not work", status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertTwo(alert_status, config, id):
    try:
        ready = await ProcessReady(id)
        logger.debug(f"Process ready : {ready}")
        cur = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        logger.debug(f"BEGIN PROCESS 2: Status id: {id} - Current status {cur}")
        
        if alert_status == AlertStatus.OPEN_2.value and ready is True:
            # First thing to do
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_2.value)
            
            trigger_job_random_id = rand_id()
            scheduler.add_job(triggerhttp, 'interval', seconds=2, id=trigger_job_random_id, args=[(trigger_job_random_id, id, LIMITED_TRIGGER_2, 2)]) # next_run_time=datetime.now()

            # Need to change the state of alert
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.OPEN_3.value)
            return "done process alert two - maybe still triggering"
        else:
            return HTTPException(detail="Alert two not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        print(ex)
        raise HTTPException(detail="Cannot process alert 2", status_code=status.HTTP_400_BAD_REQUEST)

async def ProcessAlertThree(alert_status, config, id):
    try:
        ready = await ProcessReady(id)
        logger.debug(f"Process ready : {ready}")
        cur = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        logger.debug(f"BEGIN PROCESS 3: Status id: {id} - Current status {cur}")
        
        if alert_status == AlertStatus.OPEN_3.value and ready is True:
            # First thing to do
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_3.value)
            
            trigger_job_random_id = rand_id()
            scheduler.add_job(triggerhttp, 'interval', seconds=2, id=trigger_job_random_id, args=[(trigger_job_random_id, id, LIMITED_TRIGGER_3, 3)]) # next_run_time=datetime.now()

            # Need to change the state of alert
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.OPEN_4.value)
            return "done process alert three - maybe still triggering"
        else:
            return HTTPException(detail="Alert 3 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        raise HTTPException(detail="Cannot process alert 3", status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFour(alert_status, config, id):
    try:
        ready = await ProcessReady(id)
        logger.debug(f"Process ready : {ready}")
        cur = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        logger.debug(f"BEGIN PROCESS 4: Status id: {id} - Current status {cur}")
        
        if alert_status == AlertStatus.OPEN_4.value and ready is True:
            # First thing to do
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_4.value)
            
            trigger_job_random_id = rand_id()
            scheduler.add_job(triggerhttp, 'interval', seconds=2, id=trigger_job_random_id, args=[(trigger_job_random_id, id, LIMITED_TRIGGER_4, 4)]) # next_run_time=datetime.now()

            # Need to change the state of alert
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.OPEN_5.value)
            return "done process alert four - maybe still triggering"
        else:
            return HTTPException(detail="Alert 4 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        raise HTTPException(detail="Cannot process alert 4", status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFive(alert_status, config, id):
    try:
        ready = await ProcessReady(id)
        logger.debug(f"Process ready : {ready}")
        cur = await rd.hget(CURRENT_STATUS + str(id), StatusField.STATUS.value)
        logger.debug(f"BEGIN PROCESS 5: Status id: {id} - Current status {cur}")
        
        if alert_status == AlertStatus.OPEN_5.value and ready is True:
            # First thing to do
            await rd.hset(CURRENT_STATUS + str(id), StatusField.STATUS.value, AlertStatus.PROCESSING_5.value)
            
            trigger_job_random_id = rand_id()
            scheduler.add_job(triggerhttp, 'interval', seconds=2, id=trigger_job_random_id, args=[(trigger_job_random_id, id, LIMITED_TRIGGER_5, 5)]) # next_run_time=datetime.now()
            # Delete object when done job
            await rd.delete(CURRENT_STATUS + str(id))
            return "done process alert five - maybe still triggering"
        else:
            return HTTPException(detail="Alert 5 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        raise HTTPException(detail="Cannot process alert 5", status_code=status.HTTP_400_BAD_REQUEST)
    

    

# async def test_redis():
#     try:
#         time = pickle.dumps([datetime.datetime.now(), 90])
#         await rd.set("time", time)
#         array = pickle.dumps([1,2])
#         await rd.set("array", array)
#         dict = pickle.dumps({'a':1})
#         await rd.set("dict", dict)
#         array = await rd.get("array")
#         array = pickle.loads(array)
#         dict = await rd.get("dict")
#         dict = pickle.loads(dict)
#         time = await rd.get("time")
#         time = pickle.loads(time)
#         test = await rd.get("shit")
#         print(type(test))
#         print(test)
#         print(array)
#         print(dict)
#         print(time[0])
#         print(type(time[0]))
#         return
#     except Exception as ex:
#         print(ex)
#         raise HTTPException(detail="smth", status_code=status.HTTP_400_BAD_REQUEST)