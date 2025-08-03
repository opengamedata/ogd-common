## import standard libraries
from datetime import date, datetime
from typing import Dict, Optional
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.typing import Pair

type TimestampFilterType = Optional[RangeFilter[datetime | date]]
type IndicesFilterType   = Optional[SetFilter[int] | RangeFilter[int]]

class SequencingFilterCollection:
    """Dumb struct to hold filters for timing information

    For now, it just does timestamps and session index, if need be we may come back and allow filtering by timezone offset
    """
    def __init__(self, timestamp_filter:TimestampFilterType=None, session_index_filter:IndicesFilterType=None):
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
        self._timestamp_filter     : TimestampFilterType = timestamp_filter
        self._session_index_filter : IndicesFilterType   = session_index_filter

    def __str__(self) -> str:
        ret_val = "no timestamp filters"
        if self.TimestampFilter or self.SessionIndexFilter:
            _times_str = f"time(s) {self.TimestampFilter}" if self.TimestampFilter else None
            _idxes_str = f"event index(s) {self.SessionIndexFilter}" if self.SessionIndexFilter else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"timestamp filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.TimestampFilter or self.SessionIndexFilter:
            _times_str = f"time(s) {self.TimestampFilter}" if self.TimestampFilter else None
            _idxes_str = f"event index(s) {self.SessionIndexFilter}" if self.SessionIndexFilter else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def TimestampFilter(self) -> TimestampFilterType:
        return self._timestamp_filter
    @TimestampFilter.setter
    def TimestampFilter(self, allowed_times:Optional[TimestampFilterType | slice | Pair]) -> None:
        if allowed_times is None:
            self._timestamp_filter = None
        elif isinstance(allowed_times, RangeFilter):
            self._timestamp_filter = allowed_times
        elif isinstance(allowed_times, slice):
            self._timestamp_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, slice=allowed_times)
        elif isinstance(allowed_times, tuple):
            self._timestamp_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_times[0], maximum=allowed_times[1])

    @property
    def SessionIndexFilter(self) -> IndicesFilterType:
        return self._session_index_filter
    @SessionIndexFilter.setter
    def SessionIndexFilter(self, allowed_times:Optional[IndicesFilterType | slice | Pair]) -> None:
        if allowed_times is None:
            self._session_index_filter = None
        elif isinstance(allowed_times, Filter):
            self._session_index_filter = allowed_times
        elif isinstance(allowed_times, slice):
            self._session_index_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, slice=allowed_times)
        elif isinstance(allowed_times, tuple):
            self._session_index_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_times[0], maximum=allowed_times[1])

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
