"""TableType Module
"""

# import standard libraries
from enum import IntEnum
from typing import Self

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

    @classmethod
    def FromString(cls, string:str) -> "TableType":
        match string.upper():
            case "EVENT":
                return cls.EVENT
            case "FEATURE":
                return cls.FEATURE
            case _:
                raise ValueError(f"Unrecognized table type {string}!")
