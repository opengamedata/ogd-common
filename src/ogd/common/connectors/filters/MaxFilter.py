from typing import Any
from ogd.common.connectors.filters.Filter import Filter

class MaxFilter(Filter):
    def __init__(self, maximum:Any):
        self._max = maximum

    @property
    def Max(self):
        return self._max