## import standard libraries
from typing import Dict, List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.typing import Pair

type Version = int | str | SemanticVersion
type LogFilterType     = Optional[SetFilter[Version] | RangeFilter[Version]]
type VersionFilterType = Optional[SetFilter[Version] | RangeFilter[Version]]
type BranchFilterType  = Optional[SetFilter[Version]]

class VersioningFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self, log_ver_filter:LogFilterType=None, app_ver_filter:VersionFilterType=None, branch_filter:BranchFilterType=None):
        """Constructor for the VersioningFilter structure.

        Accepts a collection of filters to be applied on versioning of data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param log_ver_filter: The filter to apply to log version, defaults to NoFilter()
        :type log_ver_filter: LogFilterType
        :param app_ver_filter: The filter to apply to app version, defaults to NoFilter()
        :type app_ver_filter: VersionFilterType
        :param branch_filter: The filter to apply to app branch, defaults to NoFilter()
        :type branch_filter: BranchFilterType
        """
        self._log_filter = log_ver_filter
        self._app_filter = app_ver_filter
        self._branch_filter = branch_filter

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        if self.LogVersionFilter or self.AppVersionFilter or self.AppBranchFilter:
            _log_str = f"log version(s) {self.LogVersionFilter}" if self.LogVersionFilter else None
            _app_str = f"app version(s) {self.AppVersionFilter}" if self.AppVersionFilter else None
            _bnc_str = f"app branch(es) {self.AppBranchFilter}"  if self.AppBranchFilter else None
            _ver_strs = ", ".join([elem for elem in [_log_str, _app_str, _bnc_str] if elem is not None])
            ret_val = f"versioning filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.LogVersionFilter or self.AppVersionFilter or self.AppBranchFilter:
            _log_str = f"log version(s) {self.LogVersionFilter}" if self.LogVersionFilter else None
            _app_str = f"app version(s) {self.AppVersionFilter}" if self.AppVersionFilter else None
            _bnc_str = f"app branch(es) {self.AppBranchFilter}"  if self.AppBranchFilter else None
            _ver_strs = " ^ ".join([elem for elem in [_log_str, _app_str, _bnc_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def AsDict(self) -> Dict[str, Filter]:
        ret_val = {}

        if self.LogVersionFilter:
            ret_val["log_versions"] = self.LogVersionFilter
        if self.AppVersionFilter:
            ret_val["app_versions"] = self.AppVersionFilter
        if self.AppBranchFilter:
            ret_val["app_branches"] = self.AppBranchFilter
        
        return ret_val

    @property
    def LogVersionFilter(self) -> LogFilterType:
        return self._log_filter
    @LogVersionFilter.setter
    def LogVersionFilter(self, allowed_versions:Optional[LogFilterType | List[Version] | Set[Version] | slice | Pair[Version, Version]]) -> None:
        if allowed_versions is None:
            self._log_filter = None
        elif isinstance(allowed_versions, Filter):
            self._log_filter = allowed_versions
        elif isinstance(allowed_versions, list) or isinstance(allowed_versions, set):
            self._log_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_versions))
        elif isinstance(allowed_versions, slice):
            self._log_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, slice=allowed_versions)
        elif isinstance(allowed_versions, tuple):
            self._log_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_versions[0], maximum=allowed_versions[1])

    @property
    def AppVersionFilter(self) -> VersionFilterType:
        return self._app_filter
    @AppVersionFilter.setter
    def AppVersionFilter(self, allowed_versions:Optional[VersionFilterType | List[Version] | Set[Version] | slice | Pair[Version, Version]]) -> None:
        if allowed_versions is None:
            self._app_filter = None
        elif isinstance(allowed_versions, Filter):
            self._app_filter = allowed_versions
        elif isinstance(allowed_versions, list) or isinstance(allowed_versions, set):
            self._app_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_versions))
        elif isinstance(allowed_versions, slice):
            self._app_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, slice=allowed_versions)
        elif isinstance(allowed_versions, tuple):
            self._app_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_versions[0], maximum=allowed_versions[1])

    @property
    def AppBranchFilter(self) -> BranchFilterType:
        return self._branch_filter
    @AppBranchFilter.setter
    def AppBranchFilter(self, allowed_branches:Optional[BranchFilterType | List[Version] | Set[Version]]) -> None:
        if allowed_branches is None:
            self._branch_filter = None
        elif isinstance(allowed_branches, SetFilter):
            self._branch_filter = allowed_branches
        elif isinstance(allowed_branches, list) or isinstance(allowed_branches, set):
            self._branch_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_branches))

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
