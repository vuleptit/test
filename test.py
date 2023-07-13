from enum import Enum
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def print_color(color: Color):
    print(color)

print_color("ab")

list = [1,2]
a,b = list
print(a,b)

if '' == None:
    print(True)
else: print(False)