## import standard libraries
from typing import Dict, List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.filters.collections.FilterCollection import FilterCollection
from ogd.common.models.enums.FilterMode import FilterMode

class EventFilterCollection(FilterCollection):
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self, event_name_filter:Filter=NoFilter(), event_code_filter:Filter=NoFilter()):
        """Constructor for the EventFilterCollection structure.

        Accepts a collection of filters to be applied on event names/codes included in the data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param event_name_filter: The filter to apply to event names, defaults to NoFilter()
        :type event_name_filter: Filter, optional
        :param event_code_filter: The filter to apply to event codes, defaults to NoFilter()
        :type event_code_filter: Filter, optional
        """
        self._event_names = event_name_filter
        self._event_codes = event_code_filter

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        _have_names = isinstance(self.EventNameFilter, NoFilter)
        _have_codes = isinstance(self.EventCodeFilter, NoFilter)
        if _have_names or _have_codes:
            _name_str = f"event name(s) {self.EventCodeFilter}" if _have_names else None
            _code_str = f"event code(s) {self.EventCodeFilter}" if _have_codes else None
            _ver_strs = ", ".join([elem for elem in [_name_str, _code_str] if elem is not None])
            ret_val = f"versioning filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        _have_names = isinstance(self.EventNameFilter, NoFilter)
        _have_codes = isinstance(self.EventCodeFilter, NoFilter)
        if _have_names or _have_codes:
            _name_str = f"event name(s) {self.EventCodeFilter}" if _have_names else None
            _code_str = f"event code(s) {self.EventCodeFilter}" if _have_codes else None
            _ver_strs = " ^ ".join([elem for elem in [_name_str, _code_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def EventNameFilter(self) -> Filter:
        return self._event_names

    @property
    def EventCodeFilter(self) -> Filter:
        return self._event_codes

    @staticmethod
    def MakeEventNameFilter(allowed_events:Optional[List[str] | Set[str]]=None) -> Filter:
        """Convenience function to set up an event name filter for use with EventFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass:
        1. If `allowed_branches` is set, *even if empty*, use it to create a `SetFilter`.
        2. If `allowed_branches` is not set, create a `NoFilter`.


        :param allowed_events: _description_, defaults to None
        :type allowed_events: Optional[List[str]  |  Set[str]], optional
        :return: _description_
        :rtype: Filter
        """
        if allowed_events is not None:
            return SetFilter(mode=FilterMode.INCLUDE, set_elements=allowed_events)
        else:
            return NoFilter()

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
