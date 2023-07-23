from fastapi import HTTPException, Depends
from common.const import LIMITED_TRIGGER_1
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import sleep
from common.utils.http_helper import http_post_endpoint, http_get_endpoint
from common.const import (CURRENT_STATUS, LIMITED_TRIGGER_1, StatusField, 
                          ENDPOINT_URL, AlertStatus, COOLING_PERIOD_TIME, 
                          IS_DISABLED_2, IS_DISABLED_3, IS_DISABLED_4, IS_DISABLED_5,
                          DEFAULT_EXCEPTION_MESSAGE, IS_COOLING_STATUS_ENABLED,
                          HTTP_STATUS_OK, AlertName)
from business_rules.logging.logging_service import write_log
from business_rules.alert.alert_crud import (remove_alert, update_alert, get_alert_by_cam_id)
from sqlalchemy.orm import Session
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from database import SessionLocal
from datetime import datetime, timedelta
from business_rules.view_models.alert_view_model import AlertViewModel

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

scheduler = AsyncIOScheduler(jobstores=jobstores)
scheduler.start()


async def SetCoolingPeriod(camera_id: str):
    try:
        db = SessionLocal()

        db_alert: AlertViewModel = get_alert_by_cam_id(db=db, cam_id=camera_id)
        db_alert.status = AlertStatus.COOLING
        db_alert.time_triggered = 0
        cooling_end_time = datetime.utcnow() + timedelta(seconds=int(COOLING_PERIOD_TIME))
        db_alert.cooling_end_time = cooling_end_time


        result = update_alert(db=db, alert=db_alert)

        if result is not None:
            write_log(
            log_str=f"The cooling period for the camera {camera_id} "
                    + f"has been set to the time: {cooling_end_time.strftime('%D/%m/%y %H:%M:%S')}"
                    + f"\nCooling period length: {COOLING_PERIOD_TIME} second(s)"
                    + f"\Result: Success", 
            camera_id=camera_id)
        else:
            write_log(
            log_str=f"The cooling period for the camera {camera_id} "
                    + f"has been set to the time: {cooling_end_time.strftime('%D/%m/%y %H:%M:S')}"
                    + f"\nCooling period length: {COOLING_PERIOD_TIME} second(s)"
                    + f"\nResult: Fail", 
            camera_id=camera_id)
        
        return result
    except Exception as ex:
        write_log(log_str=f"Exception from SetCoolingPeriod method: {str(ex)}", camera_id=camera_id)
        return DEFAULT_EXCEPTION_MESSAGE
    finally:
        db.close()

async def get_next_status(alert_name, cam_id = ''):
    try:
        db = SessionLocal()
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
            # If all other Alert is disabled -> All Alerts are done -> Remove object from database
            remove_alert(db=db, camera_id=cam_id)
    except Exception as exc:
        write_log(log_str=f'Exception from get_next_status: {str(exc)}', camera_id=cam_id)
    finally:
        db.close()
    
async def TriggerHTTP(data):
    try:
        db = SessionLocal()
        job_id, cam_id, limited, alert_name, params = data


        db_alert: AlertViewModel = get_alert_by_cam_id(db=db, cam_id=cam_id)

        current_trigger_time = db_alert.time_triggered

        write_log(log_str=f"""
BEGIN TRIGGER HTTP:
Job id: {job_id}
Camera id: {cam_id}
Current status: {str(db_alert.status)}
Limited call times: {limited}
Current call time: {str(current_trigger_time)}
Params: {str(params)}
""", camera_id=cam_id)

        # Trigger http endpoint
        res = http_get_endpoint(ENDPOINT_URL, params=params)  

        write_log(log_str=f"""
Trigger http done for the camera {cam_id}
Endpoint: {ENDPOINT_URL}
Response: {str(res)}""", camera_id=cam_id)
        
        db_alert.time_triggered += 1

        print(f'trigger http: {db_alert == None} with camid = {cam_id} and limited = {limited} and time triggered: {db_alert.time_triggered}')

        update_alert(db=db, alert=db_alert)

        if db_alert.time_triggered >= limited:
            if alert_name == AlertName.ALERT5:
                # Delete object when the Alert 5 process is done
                remove_alert(db=db, camera_id=cam_id)
                scheduler.remove_job(job_id=job_id)
                scheduler.remove_job(job_id=f'remove_record_job_{cam_id}')
                return    
            
            scheduler.remove_job(job_id=job_id)

            if alert_name == AlertName.ALERT1 and IS_COOLING_STATUS_ENABLED:
                await SetCoolingPeriod(camera_id=cam_id)
                return
        
            next_status = await get_next_status(alert_name, cam_id=cam_id)
            # Update STATUS
            db_alert.status = next_status
            db_alert.time_triggered = 0
            update_alert(db=db, alert=db_alert)
        return
    except Exception as ex:
        write_log(log_str=f"Exception from TriggerHTTP: {str(ex)}", camera_id=cam_id)
        raise HTTPException(detail=f"TriggerHTTP not work with exception {str(ex)}", status_code=400)
    finally:
        db.close()

async def remove_status_obj(data):
    try:
        db = SessionLocal()
        cam_id = data
        remove_alert(db=db, camera_id=cam_id)
        write_log(log_str=f'Removed the record for the camera. End the cycle of the camera {cam_id}', camera_id=cam_id)
    except Exception as exc:
        write_log(log_str=f'Exception from remove_status_obj: {str(exc)}', camera_id=cam_id)
    finally:
        db.close()
