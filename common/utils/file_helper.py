import os
def make_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as ex:
        return
    
def delete_dir(path):
    try:
        os.rmdir(path)
    except Exception as ex:
        return
