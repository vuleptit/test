from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from common.const import AlertStatus, AlertName

from database import Base

class Alert(Base):
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String)
    created_date = Column(DateTime)
    time_to_live = Column(DateTime)
    status = Column(Enum(AlertStatus))
    cooling_end_time = Column(DateTime, nullable=True)
    time_triggered = Column(Integer, default=0)
