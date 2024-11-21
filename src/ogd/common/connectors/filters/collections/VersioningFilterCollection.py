from ogd.common.connectors.filters.Filter import Filter
from ogd.common.connectors.filters.NoFilter import NoFilter

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

    @property
    def LogVersionFilter(self) -> Filter:
        return self._log_filter

    @property
    def AppVersionFilter(self) -> Filter:
        return self._app_filter

    @property
    def AppBranchFilter(self) -> Filter:
        return self._branch_filter
