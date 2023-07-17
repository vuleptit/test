import os
import shutil

def make_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as ex:
        return
    
def delete_dir(path):
    try:
        shutil.rmtree(path)
    except Exception as ex:
        print(str(ex))
        return
