from enum import Enum
import os

# Redis
REDIS_PORT = '6379'

# Attributes name in xml configuration file
RESET_TIME = 'resettime'
ALERT_INTERVAL_TIME = 'timeinterval'
ALERT_IS_DISABLED = False


# File_name
XML_CONFIG_FILE_NAME = 'setting.xml'

# Directory name
LOG_PATH = os.getcwd()
LOG_PATH = os.environ.get("LOG_DIRECTORY")
# Alert
class AlertName(Enum):
    ALERT1 = 'alert1'
    ALERT2 = 'alert2'
    ALERT3 = 'alert3'
    ALERT4 = 'alert4'
    ALERT5 = 'alert5'
    