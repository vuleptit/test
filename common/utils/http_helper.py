# HTTP method to call to endpoint
import requests
from sys import exc_info

def http_get_endpoint():
    try:
        url = ""
        request = requests.get(url=url)
        return request.status_code
    except Exception as ex:
        return

def http_post_endpoint():
    try:
        url = ""
        payload = []
        request = requests.post(url=url, data=payload)
        return request.status_code
    except Exception as ex:
        print(exc_info())