from typing import Any
from ogd.common.connectors.filters.Filter import Filter

class SetFilter(Filter):
    def __init__(self, set_elements:Any):
        self._set = set(set_elements)

    @property
    def Set(self):
        return self._set
