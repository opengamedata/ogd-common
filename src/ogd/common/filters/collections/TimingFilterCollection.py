## import standard libraries
from datetime import date, datetime
from typing import Dict, List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode

class TimingFilterCollection:
    """Dumb struct to hold filters for timing information

    For now, it just does timestamps and session index, if need be we may come back and allow filtering by timezone offset
    """
    def __init__(self, timestamp_filter:Filter=NoFilter(), session_index_filter:Filter=NoFilter()):
        """Constructor for the TimingFilterCollection structure.

        Accepts a collection of filters to be applied on timing of data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param log_ver_filter: The filter to apply to log version, defaults to NoFilter()
        :type log_ver_filter: Filter, optional
        :param app_ver_filter: The filter to apply to app version, defaults to NoFilter()
        :type app_ver_filter: Filter, optional
        :param branch_filter: The filter to apply to app branch, defaults to NoFilter()
        :type branch_filter: Filter, optional
        """
        self._timestamp_filter = timestamp_filter
        self._session_index_filter = session_index_filter

    def __str__(self) -> str:
        ret_val = "no timestamp filters"
        _have_times = isinstance(self.TimestampFilter, NoFilter)
        _have_idxes = isinstance(self.SessionIndexFilter, NoFilter)
        if _have_times or _have_idxes:
            _times_str = f"time(s) {self.TimestampFilter}" if _have_times else None
            _idxes_str = f"event index(s) {self.SessionIndexFilter}" if _have_idxes else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"timestamp filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        _have_times = isinstance(self.TimestampFilter, NoFilter)
        _have_idxes = isinstance(self.SessionIndexFilter, NoFilter)
        if _have_times or _have_idxes:
            _times_str = f"time(s) {self.TimestampFilter}" if _have_times else None
            _idxes_str = f"event index(s) {self.SessionIndexFilter}" if _have_idxes else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def TimestampFilter(self) -> Filter:
        return self._timestamp_filter

    @property
    def SessionIndexFilter(self) -> Filter:
        return self._session_index_filter

    @staticmethod
    def MakeTimestampFilter(minimum:Optional[date | datetime]=None, maximum:Optional[date | datetime]=None) -> Filter:
        """Convenience function to set up a timestamp filter for use with TimingFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass.
        It will choose the most specific type, as follows:
        1. If `minimum` and `maximum` are both set, use them to create a `MinMaxFilter`.
        2. If only one of `minimum` and `maximum` is set, use it to create a `MinFilter` or `MaxFilter`, respectively.
        3. If none of the inputs are set, create a `NoFilter`.

        :param minimum: _description_, defaults to None
        :type minimum: Optional[int], optional
        :param maximum: _description_, defaults to None
        :type maximum: Optional[int], optional
        :param exact_versions: _description_, defaults to None
        :type exact_versions: Optional[List[int]  |  Set[int]], optional
        :return: _description_
        :rtype: Filter
        """
        if minimum is not None and maximum is not None:
            return MinMaxFilter(mode=FilterMode.INCLUDE, minimum=minimum, maximum=maximum)
        elif minimum is not None:
            return MinFilter(mode=FilterMode.INCLUDE, minimum=minimum)
        elif maximum is not None:
            return MaxFilter(mode=FilterMode.INCLUDE, maximum=maximum)
        else:
            return NoFilter()

    @staticmethod
    def MakeSessionIndexFilter(minimum:Optional[int]=None, maximum:Optional[int]=None, exact_indices:Optional[List[int] | Set[int]]=None) -> Filter:
        """Convenience function to set up a session index filter for use with TimingFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass.
        It will choose the most specific type, as follows:
        1. If `exact_indices` is set and not empty, use it to create a `SetFilter`, ignoring `minimum` and `maximum`.
        2. If `minimum` and `maximum` are both set, use them to create a `MinMaxFilter`.
        3. If only one of `minimum` and `maximum` is set, use it to create a `MinFilter` or `MaxFilter`, respectively.
        4. If none of the inputs are set, create a `NoFilter`.

        :param minimum: _description_, defaults to None
        :type minimum: Optional[int], optional
        :param maximum: _description_, defaults to None
        :type maximum: Optional[int], optional
        :param exact_versions: _description_, defaults to None
        :type exact_versions: Optional[List[int]  |  Set[int]], optional
        :return: _description_
        :rtype: Filter
        """
        if exact_indices is not None and len(exact_indices) > 0:
                return SetFilter(mode=FilterMode.INCLUDE, set_elements=exact_indices)
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
            "timestamp": self.TimestampFilter,
            "event_session_index": self.SessionIndexFilter,
        }
