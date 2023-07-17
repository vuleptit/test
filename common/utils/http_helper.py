# HTTP method to call to endpoint
import requests
from sys import exc_info
from fastapi import HTTPException

def http_get_endpoint(url):
    try:
        url = url
        response = requests.get(url=url)
        return response
    except Exception as ex:
        return HTTPException(detail="Request failed", status_code=400)

def http_post_endpoint(url, payload):
    try:
        url = url
        payload = payload
        response = requests.post(url=url, data=payload)
        return response
    except Exception as ex:
        return HTTPException(detail="Request failed", status_code=400)