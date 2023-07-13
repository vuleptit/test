from enum import Enum
import xml.etree.ElementTree as ET
import os
from common.utils.xml_helper import find_all_alert_config_attributes, find_alert_config

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


CURRENT_STATUS = "alert_status_current"

    
COOLING_PERIOD_OBJ = "cool_period"


# XML ET TREE
et = ET.parse(XML_CONFIG_FILE_NAME)
COOLING_PERIOD = find_all_alert_config_attributes(element_tree=et, 
                                                  alert_name=AlertName.ALERT1.value, 
                                                  alert_config = AlarmConfig.COOLING_PERIOD.value, 
                                                  alert_attr=AlarmCoolingPeriod.INTERVAL.value)
TIME_TO_ACTIVATE_COOLING_PERIOD = find_all_alert_config_attributes(element_tree=et,
                                                                   alert_name=AlertName.ALERT1.value, 
                                                                   alert_config = AlarmConfig.COOLING_PERIOD.value, 
                                                                   alert_attr=AlarmCoolingPeriod.TIME_TO_ACTIVATE.value)
COOLING_STATE = find_alert_config(element_tree=et,
                                   alert_name=AlertName.ALERT1.value, 
                                   alert_config = AlarmConfig.COOLING_PERIOD.value, )
print(COOLING_STATE)


# HTTP trigger
LIMITED_TRIGGER = 3

# Logging
class MiddlewareLog(Enum):
    INTERVAL = 3
    ROTATION_FREQ = "S"

# Alert status
class AlertStatus(str, Enum):
    OPEN_1 = 'open1'
    PROCESSING_1 = 'processing1'
    OPEN_2 = 'open2'
    PROCESSING_2 = 'processing2'
    OPEN_3 = 'open3'
    PROCESSING_3 = 'processing3'
    OPEN_4 = 'open4'
    PROCESSING_4 = 'processing4'
    OPEN_5 = 'open5'
    PROCESSING_5 = 'processing5'
