"""TableType Module
"""

# import standard libraries
from enum import IntEnum

class TableType(IntEnum):
    """Enum representing the different kinds of data table from which data can be retrieved

    Namely:

    * Events
    * Features
    """
    EVENT = 1
    FEATURE = 2

    def __str__(self):
        return self.name
