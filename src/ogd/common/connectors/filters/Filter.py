from ogd.common.models.enums.FilterMode import FilterMode
class Filter:
    def __init__(self, mode:FilterMode=FilterMode.NOFILTER):
        """Constructor for base Filter class.
        By default, creates a filter equivalent to "NoFilter" class, meaning this filter will not remove any data.

        :param mode: the mode by which to apply the filter, either excluding or including all values that match the filter; defaults to FilterMode.NOFILTER
        :type mode: FilterMode, optional
        """
        self._mode = mode
    
    @property
    def FilterMode(self) -> FilterMode:
        return self._mode