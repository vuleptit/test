import logging
import requests as rq
from fastapi import APIRouter, HTTPException, Response, Request
from business_rules.alert.alert_service import (ProcessAlertOne, ProcessAlertTwo, 
                                                GetCurrentStatus, 
                                                ProcessAlertThree, ProcessAlertFour, 
                                                ProcessAlertFive)
from fastapi import Depends, status as st
import logging
from business_rules.redis.connection import redis as rd
from business_rules.alert.alert_service import create_alert
from sqlalchemy.orm import Session
from main import get_db

logger = logging.getLogger('middleware')

router = APIRouter()

@router.get("/receive-alert-1/{cam_id}")
async def receive_alert_one(request: Request, cam_id, db: Session = Depends(get_db)):
    try:
        url_params = request.query_params._dict
        current_status = await GetCurrentStatus(camera_id=cam_id)
        if current_status is not None:
            return HTTPException(detail="Another process is running", 
                                 status_code=st.HTTP_400_BAD_REQUEST)
        
        # Init the object for the new process
        create_alert(camera_id=cam_id, db=db)
        
        # Process the Alert 1
        current_status = await GetCurrentStatus(camera_id=cam_id)
        result = await ProcessAlertOne(db=db, alert_status=current_status, camera_id=cam_id, params=url_params)
        return result
    except Exception as ex:
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