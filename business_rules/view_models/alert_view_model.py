from pydantic import BaseModel
from common.const import AlertName, AlertStatus
from datetime import datetime
from typing import Union

class AlertViewModel(BaseModel):
    id: int
    camera_id: str
    status: AlertStatus
    time_to_live: datetime
    created_date: datetime
    cooling_end_time: Union[None, datetime] = None
    time_triggered: int = 0
