from datetime import datetime, timedelta

def GetCurrentTime():
    return datetime.now()

def GetTimeAfterSecond(start ,interval):
    return start + timedelta(seconds=interval)