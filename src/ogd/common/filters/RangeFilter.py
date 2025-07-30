## import standard libraries
import logging
from typing import Optional, Set
# import local files
from ogd.common.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ComparableType

class RangeFilter(Filter[ComparableType]):
    def __init__(self, mode:FilterMode, minimum:Optional[ComparableType], maximum:Optional[ComparableType]):
        super().__init__(mode=mode)
        if minimum and maximum and minimum > maximum:
            Logger.Log(f"When creating MinMaxFilter, got a minimum ({minimum}) larger than maximum ({maximum})!", level=logging.WARNING)
        self._min = minimum
        self._max = maximum

    def __str__(self) -> str:
        ret_val : str

        match self.FilterMode:
            case FilterMode.EXCLUDE:
                if self.Min and self.Max:
                    ret_val = f"outside {self.Min} to {self.Max}"
                elif self.Max:
                    ret_val = f"not under {self.Max}"
                else: # self.Min is not None
                    ret_val = f"not above {self.Min}"
            case FilterMode.INCLUDE:
                if self.Min and self.Max:
                    ret_val = f"from {self.Min} to {self.Max}"
                elif self.Max:
                    ret_val = f"under {self.Max}"
                else: # self.Min is not None
                    ret_val = f"above {self.Min}"

        return ret_val
    
    def __repr__(self) -> str:
        return f"<class {type(self).__name__} {self.FilterMode}:{self.Min}-{self.Max}>"

    @property
    def AsSet(self) -> Set[ComparableType]:
        return set()

    @property
    def Min(self) -> Optional[ComparableType]:
        return self._min

    @property
    def Max(self) -> Optional[ComparableType]:
        return self._max

    @property
    def Range(self) -> Optional[slice]:
        return slice(self.Min, self.Max)

    @staticmethod
    def FromSlice(mode:FilterMode, slice:slice) -> "RangeFilter":
        """Create a RangeFilter based on a slice object.

        This is sort of an abuse of the type, but it's a convenient way to represent a min and max where one or the other is optional.

        :param mode: _description_
        :type mode: FilterMode
        :param slice: _description_
        :type slice: slice
        :return: _description_
        :rtype: RangeFilter
        """
        return RangeFilter(mode=mode, minimum=slice.start, maximum=slice.stop)
