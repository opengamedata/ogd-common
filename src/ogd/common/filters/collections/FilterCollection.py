## import standard libraries
import abc
from typing import Any, Dict
# import local files
from ogd.common.filters.Filter import Filter

class FilterCollection:
    @property
    @abc.abstractmethod
    def AsDict(self) -> Dict[str, Filter]:
        pass

    def __init__(self):
        pass