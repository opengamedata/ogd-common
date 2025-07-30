## import standard libraries
from typing import Dict, List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.models.enums.FilterMode import FilterMode

type Version = int | str | SemanticVersion

class VersioningFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self, log_ver_filter:Filter=NoFilter(), app_ver_filter:Filter=NoFilter(), branch_filter:Filter=NoFilter()):
        """Constructor for the VersioningFilter structure.

        Accepts a collection of filters to be applied on versioning of data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param log_ver_filter: The filter to apply to log version, defaults to NoFilter()
        :type log_ver_filter: Filter, optional
        :param app_ver_filter: The filter to apply to app version, defaults to NoFilter()
        :type app_ver_filter: Filter, optional
        :param branch_filter: The filter to apply to app branch, defaults to NoFilter()
        :type branch_filter: Filter, optional
        """
        self._log_filter = log_ver_filter
        self._app_filter = app_ver_filter
        self._branch_filter = branch_filter

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        _have_log = isinstance(self.LogVersionFilter, NoFilter)
        _have_app = isinstance(self.AppVersionFilter, NoFilter)
        _have_bnc = isinstance(self.AppBranchFilter, NoFilter)
        if _have_log or _have_app or _have_bnc:
            _log_str = f"log version(s) {self.LogVersionFilter}" if _have_log else None
            _app_str = f"app version(s) {self.AppVersionFilter}" if _have_app else None
            _bnc_str = f"app branch(es) {self.AppBranchFilter}"   if _have_bnc else None
            _ver_strs = ", ".join([elem for elem in [_log_str, _app_str, _bnc_str] if elem is not None])
            ret_val = f"versioning filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        _have_log = isinstance(self.LogVersionFilter, NoFilter)
        _have_app = isinstance(self.AppVersionFilter, NoFilter)
        _have_bnc = isinstance(self.AppBranchFilter, NoFilter)
        if _have_log or _have_app or _have_bnc:
            _log_str = f"log version(s) {self.LogVersionFilter}" if _have_log else None
            _app_str = f"app version(s) {self.AppVersionFilter}" if _have_app else None
            _bnc_str = f"app branch(es) {self.AppBranchFilter}"   if _have_bnc else None
            _ver_strs = " ^ ".join([elem for elem in [_log_str, _app_str, _bnc_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def LogVersionFilter(self) -> Filter:
        return self._log_filter

    @property
    def AppVersionFilter(self) -> Filter:
        return self._app_filter

    @property
    def AppBranchFilter(self) -> Filter:
        return self._branch_filter

    @staticmethod
    def MakeLogVersionFilter(minimum:Optional[Version]=None, maximum:Optional[Version]=None, exact_versions:Optional[List[Version] | Set[Version]]=None) -> Filter:
        """Convenience function to set up a log version filter for use with VersioningFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass.
        It will choose the most specific type, as follows:
        1. If `exact_versions` is set and not empty, use it to create a `SetFilter`, ignoring `minimum` and `maximum`.
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
        return VersioningFilterCollection._makeVersionFilter(minimum=minimum, maximum=maximum, exact_versions=exact_versions)

    @staticmethod
    def MakeAppVersionFilter(minimum:Optional[Version]=None, maximum:Optional[Version]=None, exact_versions:Optional[List[Version] | Set[Version]]=None) -> Filter:
        """Convenience function to set up an app version filter for use with VersioningFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass.
        It will choose the most specific type, as follows:
        1. If `exact_versions` is set and not empty, use it to create a `SetFilter`, ignoring `minimum` and `maximum`.
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
        return VersioningFilterCollection._makeVersionFilter(minimum=minimum, maximum=maximum, exact_versions=exact_versions)

    @staticmethod
    def MakeAppBranchFilter(allowed_branches:Optional[List[str] | Set[str]]=None) -> Filter:
        """Convenience function to set up an app branch filter for use with VersioningFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass:
        1. If `allowed_branches` is set, and non-empty, use it to create a `SetFilter`.
        2. If `allowed_branches` is not set, or is empty, create a `NoFilter`.


        :param allowed_branches: _description_, defaults to None
        :type allowed_branches: Optional[List[str]  |  Set[str]], optional
        :return: _description_
        :rtype: Filter
        """
        if allowed_branches is not None:
            if len(allowed_branches) > 0:
                return SetFilter(mode=FilterMode.INCLUDE, set_elements=allowed_branches)
            else:
                return NoFilter()
        else:
            return NoFilter()

    @staticmethod
    def _makeVersionFilter(minimum:Optional[Version]=None, maximum:Optional[Version]=None, exact_versions:Optional[List[Version] | Set[Version]]=None) -> Filter:
        """Private function with the actual logic for creating a version filter.

        Just exists because the logic for MakeLogVersionFilter and MakeAppVersionFilter is the same.
        If those ever diverge, this will be removed and they'll each use own specific logic.

        :param minimum: _description_, defaults to None
        :type minimum: Optional[Version], optional
        :param maximum: _description_, defaults to None
        :type maximum: Optional[Version], optional
        :param exact_versions: _description_, defaults to None
        :type exact_versions: Optional[List[Version]  |  Set[Version]], optional
        :return: _description_
        :rtype: Filter
        """
        if exact_versions is not None and len(exact_versions) > 0:
                return SetFilter(mode=FilterMode.INCLUDE, set_elements=exact_versions)
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
            "log_version": self.LogVersionFilter,
            "app_version": self.AppVersionFilter,
            "app_branch": self.AppBranchFilter
        }
