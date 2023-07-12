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

ALERT_CONFIG = 'alert'
ALERT_STATUS = 'status'

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
class AlertStatus(Enum):
    OPEN_fOR_ALERT_1 = "open_1"
    PROCESSING_ALERT_1 = "proc_1"
    OPEN_fOR_ALERT_2 = "open_2"
    PROCESSING_ALERT_2 = "proc_2"
    OPEN_fOR_ALERT_3 = "open_3"
    PROCESSING_ALERT_3 = "proc_3"
    OPEN_fOR_ALERT_4 = "open_4"
    PROCESSING_ALERT_4 = "proc_4"
    OPEN_fOR_ALERT_5 = "open_5"
    PROCESSING_ALERT_5 = "proc_5"
    

    
    
    