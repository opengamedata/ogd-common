## import standard libraries
import abc
from typing import Optional
## import local files
from ogd.common.configs.Config import Config
from ogd.common.utils.typing import Map

## @class LocationConfig
class LocationConfig(Config):

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Location(self) -> str:
        """Gets a string representation of the full location.

        :return: A string representation of the full location.
        :rtype: str
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Location function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, other_elements:Optional[Map]=None):
        super().__init__(name=name, other_elements=other_elements)

    def __str__(self) -> str:
        return self.Location

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.Location}]"

    def __add__(self, other:"LocationConfig") -> str:
        slash = "/" if not self.Location.endswith("/") else ""
        return f"{self.Location}{slash}{other.Location}"

    def __truediv__(self, other:"LocationConfig") -> str:
        return self + other

    def __eq__(self, value:"LocationConfig") -> bool:
        return self.Location == value.Location

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
