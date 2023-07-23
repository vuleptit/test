from common.const import (AlertStatus, AlertName, TIME_TO_RESET_CYCLE, 
                          INTERVAL_1, INTERVAL_2, INTERVAL_3, INTERVAL_4, INTERVAL_5, 
                          LIMITED_TRIGGER_1, LIMITED_TRIGGER_2, LIMITED_TRIGGER_3, 
                          LIMITED_TRIGGER_4, LIMITED_TRIGGER_5, DEFAULT_EXCEPTION_MESSAGE,
                          IS_DISABLED_1, IS_DISABLED_2, IS_DISABLED_3, REMOVE_RECORD_JOB_PREFIX)
from fastapi import HTTPException
from fastapi import status
from common.utils.datetime_helper import GetCurrentTime, GetTimeAfterSecond
from common.utils.scheduler_helper import TriggerHTTP, scheduler, remove_status_obj
from business_rules.logging.logging_service import write_log
import datetime
from business_rules.view_models.alert_view_model import AlertViewModel
from sqlalchemy.orm import Session
from models.alert import Alert
from business_rules.alert.alert_crud import get_alert_by_cam_id
from business_rules.alert.alert_crud import *
    
async def GetCoolingPeriod(db: Session, camera_id) -> AlertStatus:
    try:
        db_alert: AlertViewModel = get_alert_by_id(db=db, camera_id=camera_id)
        return db_alert.status if db_alert is not None else None
    except Exception as ex:
        write_log(log_str=f'Exception from GetCoolingPeriod: {str(ex)}', camera_id=camera_id)
        return None

# Check the readiness of the Process for the Alert
async def IsFreeFromCoolingPeriod(db: Session, alert_item: AlertViewModel):
    try:
        # If the process is in Cooling period
        #   If the cooling time is not over, return exception
        #   If the cooling time is over,
        #       check if the processing can turn into the "process" status of the Alert
        if alert_item.status != AlertStatus.COOLING \
            or alert_item.cooling_end_time is None \
            or datetime.datetime.utcnow > alert_item.cooling_end_time:
            return False
        else:
            write_log("The alert is in cooling period", camera_id=alert_item.camera_id)
            return True
    except Exception as ex:
        write_log(log_str=f"Exception from IsFreeFromCoolingPeriod method: {str(ex)}", camera_id=alert_item.camera_id)
        raise HTTPException(status_code=400, detail="Exception on checking Cooling period") 

# Keep the job alive until done
async def KeepJobAlive(db: Session, interval, limited, camera_id: str):
    try:
        interval_time = interval * limited
        process_end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=interval_time)

        db_alert: AlertViewModel = get_alert_by_cam_id(db=db, cam_id=camera_id)
        if db_alert is None:
            raise HTTPException(status_code=400, detail="No record found for the camera")
        
        if db_alert.time_to_live < process_end_time:
            db_alert.time_to_live = process_end_time
            update_alert(db=db, alert=db_alert)

            scheduler.remove_job(job_id=(REMOVE_RECORD_JOB_PREFIX + camera_id))
            # Scheduler job to auto-remove record from database
            scheduler.add_job(remove_status_obj, 'date', 
                              run_date=process_end_time, 
                              args=[camera_id], id=f"{REMOVE_RECORD_JOB_PREFIX + camera_id}")

    except Exception as exc:
        write_log(log_str=f"Exception from KeepJobAlive: {str(exc)}")
        return "KeepJobAlive() not work"

# Alerts processing
async def ProcessAlertOne(db: Session, alert_status, camera_id, params):
    try:
        if alert_status == AlertStatus.OPEN_1.value:
            update_response = update_alert_status(db=db, camera_id=camera_id, new_status=AlertStatus.PROCESSING_1)
            if update_response is False:
                write_log(log_str="ProcessAlertOne: Update status of the camera record fails", camera_id=camera_id)
                raise HTTPException(status_code=400, detail="Update status of the camera record fails")
            
            await KeepJobAlive(interval=INTERVAL_1, limited=LIMITED_TRIGGER_1, camera_id=camera_id, db=db)

            # Scheduler job to trigger http
            trigger_job_random_id = f'alert1_http_job_{camera_id}'
            
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_1,
                              id=trigger_job_random_id,
                              args=[(trigger_job_random_id, camera_id, LIMITED_TRIGGER_1, AlertName.ALERT1, params)],
                              next_run_time=datetime.datetime.now())
            
            # Scheduler job to auto-remove record from database
            scheduler.add_job(remove_status_obj, 'date', 
                              run_date=GetTimeAfterSecond(GetCurrentTime(), TIME_TO_RESET_CYCLE), 
                              args=[camera_id], id=f"{REMOVE_RECORD_JOB_PREFIX + camera_id}")
            
            return "The Alert one starts the processing successfully!"
        else:
            return HTTPException(detail="The process is not opening for the Alert one", 
                                 status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        print(f'Alert 1: {str(ex)}')
        write_log(log_str=f'Exception from ProcessAlertOne: {str(ex)}', camera_id=camera_id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertTwo(camera_id, params, db: Session):
    try:
        db_alert: AlertViewModel = get_alert_by_cam_id(db=db, cam_id=camera_id)
        is_not_cooling = await IsFreeFromCoolingPeriod(alert_item=db_alert)

        if is_not_cooling is False:
            return

        write_log(log_str=f"BEGIN PROCESS 2:"
                          + f"\nCamera id: {camera_id}"
                          + f"\nCurrent status: {str(db_alert.status)}", camera_id=camera_id)
        # if CLOSE_MODE_2 == "close":
        #     return "Alert 2 is in close mode" # Not used yet

        if IS_DISABLED_2:
            write_log(log_str=f'The process is rejected because the alert 2 is disabled', camera_id=camera_id)
            return "Alert 2 is now disabled"

        if db_alert.status == AlertStatus.OPEN_2.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 2"
            update_alert_status(db=db, camera_id=camera_id, new_status=AlertStatus.PROCESSING_2)
            await KeepJobAlive(interval=INTERVAL_2, limited=LIMITED_TRIGGER_2, camera_id=camera_id, db=db)

            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert2_http_job_{camera_id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_2, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, camera_id, LIMITED_TRIGGER_2, AlertName.ALERT2, params)],
                              next_run_time=datetime.datetime.now()) 
        
            return "The Alert two starts the processing successfully!"
        else:
            return HTTPException(detail="Alert two not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertTwo: {str(ex)}', camera_id=camera_id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)

async def ProcessAlertThree(camera_id, params, db: Session):
    try:
        db_alert: AlertViewModel = get_alert_by_cam_id(db=db, cam_id=camera_id)

        is_not_cooling = await IsFreeFromCoolingPeriod(alert_item=db_alert)

        if is_not_cooling is False:
            return
        
        write_log(log_str=f"BEGIN PROCESS 3:"
                          + f"\nCamera id: {camera_id}"
                          + f"\nCurrent status: {str(db_alert.status)}", camera_id=camera_id)
        
        # if CLOSE_MODE_3 == "close":
        #     return "Alert 3 is in close mode" # Not used yet

        if IS_DISABLED_3:
            write_log(log_str=f'The process is rejected because the alert 3 is disabled', camera_id=camera_id)
            return "Alert 3 is now disabled"
        
        if db_alert.status == AlertStatus.OPEN_3.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 3"
            update_alert_status(db=db, camera_id=camera_id, new_status=AlertStatus.PROCESSING_3)
            await KeepJobAlive(interval=INTERVAL_3, limited=LIMITED_TRIGGER_3, camera_id=camera_id, db=db)

            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert3_http_job_{camera_id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_3, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, camera_id, LIMITED_TRIGGER_3, AlertName.ALERT3, params)],
                              next_run_time=datetime.datetime.now())
            
            return "The Alert three starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 3 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertThree: {str(ex)}', camera_id=camera_id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFour(camera_id, params, db: Session):
    try:
        db_alert: AlertViewModel = get_alert_by_cam_id(db=db, cam_id=camera_id)

        is_not_cooling = await IsFreeFromCoolingPeriod(alert_item=db_alert)

        if is_not_cooling is False:
            return

        write_log(log_str=f"BEGIN PROCESS 4:"
                          + f"\nCamera id: {camera_id}"
                          + f"\nCurrent status: {str(db_alert.status)}", camera_id=camera_id)
        
        # if CLOSE_MODE_4 == "close":
        #     return "Alert 4 is in close mode" # Not used yet
        
        if db_alert.status == AlertStatus.OPEN_4.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 4"
            update_alert_status(db=db, camera_id=camera_id, new_status=AlertStatus.PROCESSING_4)
            await KeepJobAlive(interval=INTERVAL_4, limited=LIMITED_TRIGGER_4, camera_id=camera_id, db=db)

            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert4_http_job_{camera_id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_4, 
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, camera_id, 
                                     LIMITED_TRIGGER_4, AlertName.ALERT4, params)],
                              next_run_time=datetime.datetime.now())

            return "The Alert four starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 4 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertFour: {str(ex)}', camera_id=camera_id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
    
async def ProcessAlertFive(camera_id, params, db: Session):
    try:
        db_alert: AlertViewModel = get_alert_by_cam_id(cam_id=camera_id, db=db)

        is_not_cooling = await IsFreeFromCoolingPeriod()

        if is_not_cooling is False:
            return

        write_log(log_str=f"BEGIN PROCESS 5:"
                          + f"\nCamera id: {camera_id}"
                          + f"\nCurrent status: {str(db_alert.status)}", camera_id=camera_id)
        
        # if CLOSE_MODE_5 == "close":
        #     return "Alert 5 is in close mode" # Not used yet
        
        if db_alert.status == AlertStatus.OPEN_5.value and is_not_cooling is True:
            # Set the status to "Processing for the alert 5"
            update_alert_status(db=db, camera_id=camera_id, new_status=AlertStatus.PROCESSING_5)
            await KeepJobAlive(interval=INTERVAL_5, limited=LIMITED_TRIGGER_5, camera_id=camera_id, db=db)
            # Create scheduler job to trigger http
            trigger_job_random_id = f'alert5_http_job_{camera_id}'
            scheduler.add_job(TriggerHTTP, 'interval', seconds=INTERVAL_5,
                              id=trigger_job_random_id, 
                              args=[(trigger_job_random_id, id, LIMITED_TRIGGER_5, AlertName.ALERT5, params)],
                              next_run_time=datetime.datetime.now())
    
            return "The Alert five starts the processing successfully!"
        else:
            return HTTPException(detail="Alert 5 not open", status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        write_log(log_str=f'Exception from ProcessAlertFive: {str(ex)}', camera_id=camera_id)
        raise HTTPException(detail=DEFAULT_EXCEPTION_MESSAGE, status_code=status.HTTP_400_BAD_REQUEST)
