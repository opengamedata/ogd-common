## import standard libraries
from typing import Dict, List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode

class EventFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self, event_name_filter:Optional[SetFilter[str]]=None, event_code_filter:Optional[SetFilter[int] | RangeFilter[int]]=None):
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
    def EventNameFilter(self) -> Optional[SetFilter]:
        """Property containing the filter for event names.

        :return: _description_
        :rtype: Optional[SetFilter]
        """
        return self._event_names
    @EventNameFilter.setter
    def EventNameFilter(self, allowed_events:Optional[SetFilter | List[str] | Set[str]]):
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
    def EventCodeFilter(self) -> Optional[SetFilter]:
        return self._event_codes
    @EventCodeFilter.setter
    def EventCodeFilter(self, allowed_events:Optional[SetFilter | List[int] | Set[int] | slice]):
        if allowed_events is None:
            self._event_codes = None
        elif isinstance(allowed_events, SetFilter):
            self._event_codes = allowed_events
        elif isinstance(allowed_events, list) or isinstance(allowed_events, set):
            self._event_codes = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_events))

    @staticmethod
    def MakeEventCodeFilter(minimum:Optional[int]=None, maximum:Optional[int]=None, exact_codes:Optional[List[int] | Set[int]]=None) -> Filter:
        """Convenience function to set up an event code filter for use with EventFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass.
        It will choose the most specific type, as follows:
        1. If `exact_codes` is set, use it to create a `SetFilter`, *even if empty*, ignoring `minimum` and `maximum`.
        2. If `minimum` and `maximum` are both set, use them to create a `MinMaxFilter`.
        3. If only one of `minimum` and `maximum` is set, use it to create a `MinFilter` or `MaxFilter`, respectively.
        4. If none of the inputs are set, create a `NoFilter`.

        :param minimum: _description_, defaults to None
        :type minimum: Optional[int], optional
        :param maximum: _description_, defaults to None
        :type maximum: Optional[int], optional
        :param exact_codes: _description_, defaults to None
        :type exact_codes: Optional[List[int]  |  Set[int]], optional
        :return: _description_
        :rtype: Filter
        """
        # Only check if exact_codes is not None. If it's empty, we'll assume filter wants to remove all events.
        if exact_codes is not None:
                return SetFilter(mode=FilterMode.INCLUDE, set_elements=exact_codes)
        elif minimum is not None and maximum is not None:
            return MinMaxFilter(mode=FilterMode.INCLUDE, minimum=minimum, maximum=maximum)
        elif minimum is not None:
            return MinFilter(mode=FilterMode.INCLUDE, minimum=minimum)
        elif maximum is not None:
            return MaxFilter(mode=FilterMode.INCLUDE, maximum=maximum)
        else:
            return NoFilter()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _asDict(self) -> Dict[str, Filter]:
        return {
            "event_name": self.EventNameFilter,
            "event_code": self.EventCodeFilter
        }
