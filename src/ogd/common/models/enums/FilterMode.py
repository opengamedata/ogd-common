# import standard libraries
from enum import IntEnum

class FilterMode(IntEnum):
    INCLUDE = 1
    EXCLUDE = 2

    def __str__(self):
        return self.name
