import logging.handlers
import datetime
import os
from common.utils.file_helper import make_dir
from common.const import LOG_PATH

# Logger will call this function on rotating log

def write_log(log_str: str, camera_id: str = ''):
    current_time = datetime.datetime.now()

    # Create folder
    make_dir('logs')
    date_folder_name = current_time.strftime('%Y_%m_%d')
    make_dir(f"logs/{date_folder_name}")



    # Write log
    f = open(f"{os.getcwd()}/logs/{date_folder_name}/{camera_id}.txt", "a")
    f.writelines("\n===============================\n")
    f.writelines("Start time: " + current_time.strftime('%d/%m/%Y %H:%M:%S') + "\n")
    f.writelines(log_str)
    f.writelines("\n===============================\n")
