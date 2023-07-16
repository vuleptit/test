import time
import logging
import logging.handlers
import datetime
import os
from common.utils.file_helper import make_dir
from common.const import LOG_PATH

# Logger will call this function on rotating log

def ChangeFileNameOnRotating(default_name):
    file_name = os.path.split(default_name)[1]
    daily_folder = datetime.datetime.now().strftime('%Y-%m-%d') 
    hourly_folder = datetime.datetime.now().strftime('%H-%M')
    folder_path = os.path.join(daily_folder, hourly_folder)
    folder = os.path.join(LOG_PATH, folder_path)
    
    try:
        make_dir(folder)
    except:
        pass
    return os.path.join(folder, file_name)

def InitRotatingLog(filename, rotation_freq, interval):
    try:
        logging_level = logging.DEBUG
        
        handler = logging.handlers.TimedRotatingFileHandler(filename=filename, when=rotation_freq, interval=interval)
        handler.namer = ChangeFileNameOnRotating
        
        # suffix format
        handler.suffix = "%H-%M-%S.log"
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        
        # name logger
        logger = logging.getLogger("middleware")
        logger.addHandler(handler)
        logger.setLevel(logging_level)
        return logger, handler
    except Exception as ex:
        logging.exception("Unhandled error\n{}".format(ex))
        raise