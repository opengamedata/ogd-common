## import standard libraries
import abc
from typing import Dict
# import local files
from ogd.common.connectors.filters.Filter import Filter

class FilterCollection:
    @abc.abstractmethod
    def _asDict(self):
        pass

    def __init__(self):
        pass

    @property
    def AsDict(self) -> Dict[str, Filter]:
        return self._asDict()