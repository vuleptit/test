# HTTP method to call to endpoint
import requests
from sys import exc_info
from fastapi import HTTPException

def http_get_endpoint(url):
    try:
        url = url
        request = requests.get(url=url)
        return request
    except Exception as ex:
        return HTTPException(detail="requests failed", status_code=400)

def http_post_endpoint(url, payload):
    try:
        url = url
        payload = payload
        request = requests.post(url=url, data=payload)
        return request.status_code
    except Exception as ex:
        return HTTPException(detail="requests failed", status_code=400)