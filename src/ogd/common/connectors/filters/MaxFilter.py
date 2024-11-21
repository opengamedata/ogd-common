from typing import Any
from ogd.common.connectors.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class MaxFilter(Filter):
    def __init__(self, mode:FilterMode, maximum:Any):
        super().__init__(mode=mode)
        self._max = maximum

    @property
    def Max(self):
        return self._max