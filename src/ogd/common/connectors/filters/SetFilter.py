## import standard libraries
import logging
from typing import Any
# import local files
from ogd.common.utils.Logger import Logger
from ogd.common.connectors.filters.Filter import Filter

class SetFilter(Filter):
    def __init__(self, set_elements:Any):
        if len(set_elements) == 0:
            Logger.Log("Creating a SetFilter from an empty set! This will be intepreted as filtering out all values, not as an empty filter that allows all values to pass! For the latter case, use the NoFilter class.", logging.WARNING)
        self._set = set(set_elements)

    @property
    def Set(self):
        return self._set
