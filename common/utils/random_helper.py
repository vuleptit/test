import string
import random

def rand_id(length=6):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length)) 
    print(res)
    return str(res)