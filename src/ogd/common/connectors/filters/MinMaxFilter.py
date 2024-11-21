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

    @property
    def Min(self):
        return self._min

    @property
    def Max(self):
        return self._max
