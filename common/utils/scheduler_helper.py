from common.const import LIMITED_TRIGGER
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from time import sleep

scheduler = BackgroundScheduler()
scheduler.start()


def myfunc(id):
    try:
        # time of execution must not last longer than the job interval
        sleep(1)
        print("haha")
        scheduler.remove_job(job_id=id)
    except Exception as ex:
        print(ex)
        scheduler.remove_job(job_id=id)
    
    