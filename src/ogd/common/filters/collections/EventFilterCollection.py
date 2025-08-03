## import standard libraries
from typing import Any, Dict, List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.typing import Pair

class EventFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    type NameFilterType = Optional[SetFilter[str]]
    type CodeFilterType = Optional[SetFilter[int] | RangeFilter[int]]

    def __init__(self, event_name_filter:NameFilterType=None, event_code_filter:CodeFilterType=None):
        """Constructor for the EventFilterCollection structure.

        Accepts a collection of filters to be applied on event names/codes included in the data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param event_name_filter: The filter to apply to event names, defaults to NoFilter()
        :type event_name_filter: Filter, optional
        :param event_code_filter: The filter to apply to event codes, defaults to NoFilter()
        :type event_code_filter: Filter, optional
        """
        self._event_names : Optional[SetFilter[str]] = event_name_filter
        self._event_codes = event_code_filter

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        if self.EventNameFilter or self.EventCodeFilter:
            _name_str = f"event name(s) {self.EventCodeFilter}" if self.EventNameFilter else None
            _code_str = f"event code(s) {self.EventCodeFilter}" if self.EventCodeFilter else None
            _ver_strs = ", ".join([elem for elem in [_name_str, _code_str] if elem is not None])
            ret_val = f"versioning filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.EventNameFilter is not None or self.EventCodeFilter is not None:
            _name_str = repr(self.EventNameFilter) if self.EventNameFilter else None
            _code_str = repr(self.EventCodeFilter) if self.EventCodeFilter else None
            _ver_strs = " ^ ".join([elem for elem in [_name_str, _code_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def EventNameFilter(self) -> NameFilterType:
        """Property containing the filter for event names.

        :return: _description_
        :rtype: Optional[SetFilter]
        """
        return self._event_names
    @EventNameFilter.setter
    def EventNameFilter(self, allowed_events:Optional[NameFilterType | List[str] | Set[str]]):
        """Can be conveniently set from an existing filter, or collection of event names.

        If set this way, the filter is assumed to be an "inclusion" filter.

        :param allowed_events: _description_, defaults to None
        :type allowed_events: Optional[List[str]  |  Set[str]], optional
        :return: _description_
        :rtype: Filter
        """
        if allowed_events is None:
            self._event_names = None
        elif isinstance(allowed_events, SetFilter):
            self._event_names = allowed_events
        elif isinstance(allowed_events, list) or isinstance(allowed_events, set):
            self._event_names = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_events))

    @property
    def EventCodeFilter(self) -> CodeFilterType:
        return self._event_codes
    @EventCodeFilter.setter
    def EventCodeFilter(self, allowed_events:Optional[CodeFilterType | List[int] | Set[int] | slice | Pair[int, int]]):
        if allowed_events is None:
            self._event_codes = None
        elif isinstance(allowed_events, Filter):
            self._event_codes = allowed_events
        elif isinstance(allowed_events, list) or isinstance(allowed_events, set):
            self._event_codes = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_events))
        elif isinstance(allowed_events, slice):
            self._event_codes = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, slice=allowed_events)
        elif isinstance(allowed_events, tuple):
            self._event_codes = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_events[0], maximum=allowed_events[1])

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
