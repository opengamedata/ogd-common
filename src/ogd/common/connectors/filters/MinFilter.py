from typing import Any
from ogd.common.connectors.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class MinFilter(Filter):
    def __init__(self, mode:FilterMode, minimum:Any):
        self._min = minimum
        super().__init__(mode=mode)

    def __str__(self) -> str:
        _exclude_clause = "not " if self.FilterMode == FilterMode.EXCLUDE else ""
        return f"{_exclude_clause}.above {self.Min}"
    
    def __repr__(self) -> str:
        return f"<class {type(self).__name__} {self.FilterMode}:{self.Min}>"

    @property
    def Min(self):
        return self._min
