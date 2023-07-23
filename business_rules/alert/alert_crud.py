from common.const import (AlertStatus, TIME_TO_RESET_CYCLE)
from fastapi import HTTPException
from business_rules.logging.logging_service import write_log
import datetime
from business_rules.view_models.alert_view_model import AlertViewModel
from sqlalchemy.orm import Session
from models.alert import Alert

def get_alert_by_id(db: Session, id: int) -> AlertViewModel:
    return db.query(Alert).filter(Alert.id == id).first()

def get_alert_by_cam_id(db: Session, cam_id: int) -> Alert:
    try:
        alert_item: Alert = db.query(Alert).filter(Alert.camera_id == cam_id).first()
        return map_to_view_model(alert_item)
    except Exception as exc:
        print('Exception: ' + str(exc))
        return None

def update_alert(db: Session, alert: AlertViewModel):
    try:
        alert_in_db: Alert = db.query(Alert).filter(Alert.camera_id == alert.camera_id).first()
        if alert_in_db == None:
            return None

        alert_in_db.status = alert.status
        alert_in_db.time_to_live = alert.time_to_live
        alert_in_db.time_triggered = alert.time_triggered
        alert_in_db.cooling_end_time = alert.cooling_end_time
        db.commit()
        db.refresh(alert_in_db)
        return alert_in_db
    except Exception as exc:
        write_log(f"Exception from update_alert: {str(exc)}")

def create_alert(db: Session, camera_id: str):
    try:
        ttl_in_second = TIME_TO_RESET_CYCLE

        alert = Alert()
        alert.created_date = datetime.datetime.utcnow()
        alert.camera_id = camera_id
        alert.time_triggered = 0
        alert.time_to_live = datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_in_second)
        alert.status = AlertStatus.OPEN_1
        alert.cooling_end_time = None
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    except Exception as exc:
        print(f'ex from create: {str(exc)}')

        write_log(f"Exception from create_alert: {str(exc)}", camera_id=camera_id)
        return None

def remove_alert(db: Session, camera_id: str) -> bool:
    try:
        alerts_query = db.query(Alert).filter(Alert.camera_id == camera_id)
        if alerts_query is not None and alerts_query.count() > 0:
            alerts_query.delete()
            db.commit()
        return True
    except Exception as exc:
        write_log(f"Exception from remove_alert: {str(exc)}")
        return False

def update_alert_status(db: Session, camera_id: str, new_status: AlertStatus) -> bool:
    try:
        alert_item = db.query(Alert).filter(Alert.camera_id == camera_id).first()

        if alert_item is None:
            return False
        
        alert_item.status = new_status
        db.commit()
        return True
    except Exception as exc:
        write_log(f"Exception from update_alert_status: {str(exc)}")
        return False
    
def remove_out_of_date_record(db: Session):
    # Delete the alerts that are out of date
    current_time = datetime.datetime.utcnow()
    out_of_date_alerts = db.query(Alert).filter(Alert.time_to_live <= current_time)
    if out_of_date_alerts is not None and out_of_date_alerts.count() > 0:
        out_of_date_alerts.delete()
        db.commit()
    
def map_to_view_model(alert: Alert):
    if alert is None:
        return None
    
    view_model = AlertViewModel(id=alert.id, camera_id=alert.camera_id, status=alert.status, 
                                time_to_live=alert.time_to_live, created_date=alert.created_date, 
                                cooling_end_time=alert.cooling_end_time, time_triggered=alert.time_triggered)
    return view_model

