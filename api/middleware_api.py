import logging
import requests as rq
from fastapi import APIRouter, HTTPException, Response, Request
from business_rules.alert.alert_service import (ProcessAlertOne, ProcessAlertTwo, ProcessAlertThree, 
                                                ProcessAlertFour, ProcessAlertFive)
from fastapi import Depends, status as st
import logging
from business_rules.alert.alert_crud import create_alert, get_alert_by_cam_id
from sqlalchemy.orm import Session
from database import get_db
from business_rules.view_models.alert_view_model import AlertViewModel
from models.alert import Alert

logger = logging.getLogger('middleware')

router = APIRouter()

@router.get("/receive-alert-1/{cam_id}")
async def receive_alert_one(request: Request, cam_id, db: Session = Depends(get_db)):
    try:
        url_params = request.query_params._dict

        db_alert: AlertViewModel = get_alert_by_cam_id(cam_id=cam_id, db=db)

        if db_alert is not None:
            return HTTPException(detail="Another process is running", 
                                 status_code=st.HTTP_400_BAD_REQUEST)
        
        # Init the object for the new process
        db_alert = create_alert(camera_id=cam_id, db=db)
        
        # Process the Alert 1
        result = await ProcessAlertOne(db=db, alert_status=db_alert.status, camera_id=cam_id, params=url_params)
        return result
    except Exception as ex:
        print(f'Alert 1: {str(ex)}')
        raise HTTPException(status_code=400, detail="receive_alert_one not work")

@router.get("/receive-alert-2/{cam_id}")
async def receive_alert_two(request: Request, cam_id, db: Session = Depends(get_db)):
    try:
        url_params = request.query_params._dict
        result = await ProcessAlertTwo(camera_id=cam_id, params=url_params, db=db)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_two not work")

@router.get("/receive-alert-3/{cam_id}")
async def receive_alert_three(request: Request, cam_id, db: Session = Depends(get_db)):
    try:
        url_params = request.query_params._dict
        result = await ProcessAlertThree(id=cam_id, params=url_params, db=db)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_3 not work")

@router.get("/receive-alert-4/{cam_id}")
async def receive_alert_four(request: Request, cam_id):
    try:
        url_params = request.query_params._dict
        result = await ProcessAlertFour(id=cam_id, params=url_params)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_4 not work")

@router.get("/receive-alert-5/{cam_id}")
async def receive_alert_five(request: Request, cam_id):
    try:
        url_params = request.query_params._dict
        result = await ProcessAlertFive(id=cam_id, params=url_params)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail="receive_alert_5 not work")

@router.get('/free')
def free():
    return Response(content='a', status_code=200)

@router.get('/alert/{cam_id}')
def free(cam_id, db: Session = Depends(get_db)):
    alert = get_alert_by_cam_id(cam_id=cam_id, db=db)
    alert_item = db.query(Alert).filter(Alert.id > 0).all()
    return Response(content=str([alert]), status_code=200)

@router.post('/delete-alert/{cam_id}')
def free(cam_id, db: Session = Depends(get_db)):
    alert = get_alert_by_cam_id(cam_id=cam_id, db=db)
    alert_item = db.query(Alert).filter(Alert.id > 0).all()
    return Response(content=str([alert]), status_code=200)
