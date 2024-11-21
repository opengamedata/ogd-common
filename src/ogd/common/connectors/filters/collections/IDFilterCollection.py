from ogd.common.connectors.filters.SetFilter import SetFilter
from ogd.common.connectors.filters.NoFilter import NoFilter

type IDFilter = SetFilter | NoFilter

class IDFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self, session_filter:IDFilter=NoFilter(), player_filter:IDFilter=NoFilter()):
        self._session_filter = session_filter
        self._player_filter = player_filter

    @property
    def SessionFilter(self) -> IDFilter:
        return self._session_filter

    @property
    def PlayerFilter(self) -> IDFilter:
        return self._player_filter
