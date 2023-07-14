from enum import Enum
import xml.etree.ElementTree as ET
import os
from common.utils.xml_helper import find_alert_config_attributes, find_config, find_reset_time

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
# setting.xml comfig name 
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

class StatusField(str, Enum):
    STATUS = "status"
    TRIGGER_TIME = "trigger_time"
    COOLING = "cooling"

# Redis object name
ALERT_CONFIG_OBJ = 'alert'


CURRENT_STATUS = "alert_status_current"


COOLING_PERIOD_OBJ = "cool_period"


# XML ET TREE
et = ET.parse(XML_CONFIG_FILE_NAME)

COOLING_PERIOD = find_alert_config_attributes(element_tree = et, 
                                                  alert_name = AlertName.ALERT1.value, 
                                                  alert_config = AlarmConfig.COOLING_PERIOD.value, 
                                                  alert_attr = AlarmCoolingPeriod.INTERVAL.value)
# COOLING_TIME = find_alert_config_attributes(element_tree = et,
#                                             alert_name = AlertName.ALERT1.value, 
#                                             alert_config = AlarmConfig.COOLING_PERIOD.value, 
#                                             alert_attr = AlarmCoolingPeriod.TIME_TO_ACTIVATE.value)
COOLING_STATE = find_config(element_tree = et,
                            alert_name = AlertName.ALERT1.value,
                            alert_config = AlarmConfig.COOLING_PERIOD.value)

TIME_TO_RESET_CYCLE = find_reset_time(element_tree=et)

# HTTP trigger config
LIMITED_TRIGGER_1 = int(find_config(element_tree=et,
                                alert_name=AlertName.ALERT1.value,
                                alert_config=AlarmConfig.REPEAT.value))
LIMITED_TRIGGER_2 = int(find_config(element_tree=et,
                                alert_name=AlertName.ALERT2.value,
                                alert_config=AlarmConfig.REPEAT.value))
LIMITED_TRIGGER_3 = int(find_config(element_tree=et,
                                alert_name=AlertName.ALERT3.value,
                                alert_config=AlarmConfig.REPEAT.value))
LIMITED_TRIGGER_4 = int(find_config(element_tree=et,
                                alert_name=AlertName.ALERT4.value,
                                alert_config=AlarmConfig.REPEAT.value))
LIMITED_TRIGGER_5 = int(find_config(element_tree=et,
                                alert_name=AlertName.ALERT5.value,
                                alert_config=AlarmConfig.REPEAT.value))

INTERVAL_1 = int(find_config(element_tree=et,
                        alert_name=AlertName.ALERT1.value,
                        alert_config=AlarmConfig.TIME_INTERVAL.value))
INTERVAL_2 = int(find_config(element_tree=et,
                        alert_name=AlertName.ALERT2.value,
                        alert_config=AlarmConfig.TIME_INTERVAL.value))
INTERVAL_3 = int(find_config(element_tree=et,
                        alert_name=AlertName.ALERT3.value,
                        alert_config=AlarmConfig.TIME_INTERVAL.value))
INTERVAL_4 = int(find_config(element_tree=et,
                        alert_name=AlertName.ALERT4.value,
                        alert_config=AlarmConfig.TIME_INTERVAL.value))
INTERVAL_5 = int(find_config(element_tree=et,
                        alert_name=AlertName.ALERT5.value,
                        alert_config=AlarmConfig.TIME_INTERVAL.value))

CLOSEMODE_2 = str(find_config(element_tree=et,
                        alert_name=AlertName.ALERT2.value,
                        alert_config=AlarmConfig.CLOSEMODE.value))
CLOSEMODE_3 = str(find_config(element_tree=et,
                        alert_name=AlertName.ALERT3.value,
                        alert_config=AlarmConfig.CLOSEMODE.value))
CLOSEMODE_4 = str(find_config(element_tree=et,
                        alert_name=AlertName.ALERT4.value,
                        alert_config=AlarmConfig.CLOSEMODE.value))
CLOSEMODE_5 = str(find_config(element_tree=et,
                        alert_name=AlertName.ALERT5.value,
                        alert_config=AlarmConfig.CLOSEMODE.value))

# Logging
class MiddlewareLog(Enum):
    INTERVAL = 3
    ROTATION_FREQ = "S"


# Enpoint url
ENDPOINT_URL = "http://127.0.0.1:8665/trigger/free"
