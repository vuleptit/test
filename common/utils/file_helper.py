import os
def make_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as ex:
        return