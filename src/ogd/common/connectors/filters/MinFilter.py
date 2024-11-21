from typing import Any
from ogd.common.connectors.filters.Filter import Filter

class MinFilter(Filter):
    def __init__(self, minimum:Any):
        self._min = minimum

    @property
    def Min(self):
        return self._min
