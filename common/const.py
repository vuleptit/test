from enum import Enum
import xml.etree.ElementTree as ET
import os
from common.utils.xml_helper import find_all_alert_config_attributes

# Redis
REDIS_PORT = '6379'

# Attributes name in xml configuration file
RESET_TIME = 'resettime'
ALERT_INTERVAL_TIME = 'timeinterval'
ALERT_IS_DISABLED = False

# File_name
XML_CONFIG_FILE_NAME = 'setting.xml'
TEMPORARY_LOG_FILE_NAME = "tmp"

# Directory name
LOG_PATH = os.environ.get('LOG_DIRECTORY')

class AlarmConfig(Enum):
    COOLING_PERIOD = "alarmcoolingperiod"
    REPEAT = "repeat"
    TIME_INTERVAL = "timeinterval"
    DISABLE = "disable"
    CLOSEMODE = "closemode"

class AlarmCoolingPeriod(Enum):
    INTERVAL = "interval"
    TIME_TO_ACTIVATE = "timetoactivate"

# Alert
class AlertName(Enum):
    ALERT1 = 'alert1'
    ALERT2 = 'alert2'
    ALERT3 = 'alert3'
    ALERT4 = 'alert4'
    ALERT5 = 'alert5'

# Redis object name
ALERT_CONFIG_OBJ = 'alert'
class AlertStatusObject(str, Enum):
    CURRENT = "alert_status_current"
    ALERT1 = "alert1_status"
    ALERT2 = "alert2_status"
    ALERT3 = "alert3_status"
    ALERT5 = "alert4_status"
    ALERT4 = "alert5_status"
    
COOLING_PERIOD_OBJ = "cool_period"

et = ET.parse(XML_CONFIG_FILE_NAME)
COOLING_PERIOD = find_all_alert_config_attributes(element_tree=et, 
                                                  alert_name=AlertName.ALERT1.value, 
                                                  alert_config = AlarmConfig.COOLING_PERIOD.value, 
                                                  alert_attr=AlarmCoolingPeriod.INTERVAL.value)
TIME_TO_ACTIVATE_COOLING_PERIOD = find_all_alert_config_attributes(element_tree=et,
                                                                   alert_name=AlertName.ALERT1.value, 
                                                                   alert_config = AlarmConfig.COOLING_PERIOD.value, 
                                                                   alert_attr=AlarmCoolingPeriod.TIME_TO_ACTIVATE.value)

# HTTP trigger
LIMITED_TRIGGER = 3

# Logging
class MiddlewareLog(Enum):
    INTERVAL = 3
    ROTATION_FREQ = "S"

# Alert status
class AlertStatus(str, Enum):
    OPEN = 'open'
    PROCESSING = 'processing'