from typing import Any
from ogd.common.connectors.filters.Filter import Filter

class MinMaxFilter(Filter):
    def __init__(self, minimum:Any, maximum:Any):
        self._min = minimum
        self._max = maximum

    @property
    def Min(self):
        return self._min

    @property
    def Max(self):
        return self._max
