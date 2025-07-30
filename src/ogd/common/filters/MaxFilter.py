from typing import Any
from ogd.common.connectors.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class MaxFilter(Filter):
    def __init__(self, mode:FilterMode, maximum:Any):
        super().__init__(mode=mode)
        self._max = maximum

    def __str__(self) -> str:
        _exclude_clause = "not " if self.FilterMode == FilterMode.EXCLUDE else ""
        return f"{_exclude_clause}under {self.Max}"
    
    def __repr__(self) -> str:
        return f"<class {type(self).__name__} {self.FilterMode}:{self.Max}>"

    @property
    def Max(self):
        return self._max