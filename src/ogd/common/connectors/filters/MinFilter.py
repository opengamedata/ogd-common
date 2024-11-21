from typing import Any
from ogd.common.connectors.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class MinFilter(Filter):
    def __init__(self, mode:FilterMode, minimum:Any):
        self._min = minimum
        super().__init__(mode=mode)

    @property
    def Min(self):
        return self._min
