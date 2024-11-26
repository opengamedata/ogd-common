## import standard libraries
import logging
from typing import Any
# import local files
from ogd.common.utils.Logger import Logger
from ogd.common.connectors.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class MinMaxFilter(Filter):
    def __init__(self, mode:FilterMode, minimum:Any, maximum:Any):
        super().__init__(mode=mode)
        if minimum > maximum:
            Logger.Log(f"When creating MinMaxFilter, got a minimum ({minimum}) larger than maximum ({maximum})!", level=logging.WARNING)
        self._min = minimum
        self._max = maximum

    def __str__(self) -> str:
        return f"{self.Min} to {self.Max}"
    
    def __repr__(self) -> str:
        return f"<class {type(self).__name__} {self.FilterMode}:{self.Min}-{self.Max}>"

    @property
    def Min(self):
        return self._min

    @property
    def Max(self):
        return self._max
