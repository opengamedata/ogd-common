## import standard libraries
import logging
from typing import Any, Set
# import local files
from ogd.common.utils.Logger import Logger
from ogd.common.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class SetFilter(Filter[Any]):
    def __init__(self, mode:FilterMode, set_elements:Any):
        super().__init__(mode=mode)
        if len(set_elements) == 0:
            Logger.Log("Creating a SetFilter from an empty set! This will be intepreted as filtering out all values, not as an empty filter that allows all values to pass! For the latter case, use the NoFilter class.", logging.WARNING)
        self._set = set(set_elements)

    def __str__(self) -> str:
        _exclude_clause = "not in " if self.FilterMode == FilterMode.EXCLUDE else ""
        return f"{_exclude_clause}set of {len(self._set)} elements"
    
    def __repr__(self) -> str:
        _types = set(type(elem).__name__ for elem in self.AsSet)
        _type_str = " | ".join(_types)
        return f"<class {type(self).__name__} {self.FilterMode}:Set[{_type_str}] with {len(self.AsSet)} elements>"

    @property
    def AsSet(self) -> Set[Any]:
        return self._set

    @property
    def Min(self) -> None:
        return None

    @property
    def Max(self) -> None:
        return None
