from enum import Enum
from pydantic import str
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def print_color(color: Color):
    print(color)

print_color("ab")