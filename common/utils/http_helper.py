# HTTP method to call to endpoint
import requests
from sys import exc_info
from fastapi import HTTPException

def http_get_endpoint(url, params=None):
    try:
        url = url
        res = requests.get(url=url)
        res = requests.get(url=url, params=params)
        return res.json()
    except Exception as ex:
        return HTTPException(detail="Request failed", status_code=400)

def http_post_endpoint(url, payload):
    try:
        url = url
        payload = payload
        res = requests.post(url=url, data=payload)
        return res.json()
    except Exception as ex:
        return HTTPException(detail="Request failed", status_code=400)