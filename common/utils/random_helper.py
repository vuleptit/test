import string
import random

def rand_id(length=8):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return str(res)