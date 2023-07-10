from fastapi import APIRouter, HTTPException, Response
from business_rules.redis.connection import redis as rd
from ast import literal_eval
from typing import Union
from pydantic import BaseModel
import logging


logger = logging.getLogger('middleware')

class DataModel(BaseModel):
    code: int
    class Config:
        orm_mode = True

router = APIRouter()

@router.get('/')
async def get_set_redis():
    try:
        logger.info('Before getting alert config')
        config = await rd.get('alert')
        logger.info('After getting alert config')
        config = literal_eval(config.decode('utf-8'))
        
    except Exception as ex:
        print(ex)
    return config
    
@router.get('/endpoint')
async def get_endpoint(data: DataModel):
    try:
        data = data
    except Exception as ex:
        print(ex)
        raise HTTPException("Something went wrong") 
    
@router.post('/endpoint/')
async def post_endpoint(data: DataModel):
    try:
        data = data
    except Exception as ex:
        print(ex)
        raise HTTPException("Something went wrong") 