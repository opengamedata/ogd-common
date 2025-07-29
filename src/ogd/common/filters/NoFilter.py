from ogd.common.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class NoFilter(Filter):
    def __init__(self):
        super().__init__(mode=FilterMode.NOFILTER)

    def __str__(self) -> str:
        return f"no filter"
