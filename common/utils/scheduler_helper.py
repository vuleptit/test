from common.const import LIMITED_TRIGGER
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import sleep
from common.utils.http_helper import http_post_endpoint
from business_rules.redis.connection import redis as rd
from common.const import CURRENT_STATUS, LIMITED_TRIGGER, StatusField
scheduler = BackgroundScheduler()
scheduler.start()


async def triggerhttp(data):
    try:
        jobid, camid = data
        print("((((((((((((((((((((((()))))))))))))))))))))))")
        print(jobid, camid)
        # time of execution must not last longer than the job interval
        # http_post_endpoint(url=url, payload=data)
        sleep(0.5)
        trigger_time_obj = str(CURRENT_STATUS + str(camid))
        current_trigger_time = await rd.hget(trigger_time_obj, StatusField.TRIGGER_TIME)
        
        if current_trigger_time == LIMITED_TRIGGER:
            scheduler.remove_job(job_id=jobid)
        else:
            update_trigger_time = int(current_trigger_time) +1
            await rd.set(trigger_time_obj, update_trigger_time)
    except Exception as ex:
        scheduler.remove_job(job_id=jobid)
        
def remove_status_obj(data):
    print("hello")
    jobid, camid = data
    return
    
    