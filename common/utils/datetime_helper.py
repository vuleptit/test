from datetime import datetime, timedelta

def GetCurrentTime():
    return datetime.now()

def GetTimeAfterInterval(start ,interval):
    return start + timedelta(seconds=interval)