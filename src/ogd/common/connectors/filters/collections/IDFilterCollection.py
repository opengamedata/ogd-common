## import standard libraries
from typing import Dict, List, Optional, Set
# import local files
from ogd.common.connectors.filters import *
from ogd.common.connectors.filters.collections.FilterCollection import FilterCollection
from ogd.common.models.enums.FilterMode import FilterMode

type IDFilter = SetFilter | NoFilter

class IDFilterCollection(FilterCollection):
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self, session_filter:IDFilter=NoFilter(), player_filter:IDFilter=NoFilter()):
        self._session_filter = session_filter
        self._player_filter = player_filter

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        _have_sess = isinstance(self.SessionFilter, NoFilter)
        _have_ply = isinstance(self.PlayerFilter, NoFilter)
        if _have_sess or _have_ply:
            _sess_str = f"session(s) {self.SessionFilter}" if _have_sess else None
            _ply_str = f"player(s) {self.PlayerFilter}" if _have_ply else None
            _ver_strs = ", ".join([elem for elem in [_sess_str, _ply_str] if elem is not None])
            ret_val = f"event filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        _have_sess = isinstance(self.SessionFilter, NoFilter)
        _have_ply = isinstance(self.PlayerFilter, NoFilter)
        if _have_sess or _have_ply:
            _sess_str = f"session(s) {self.SessionFilter}" if _have_sess else None
            _ply_str = f"player(s) {self.PlayerFilter}" if _have_ply else None
            _ver_strs = " ^ ".join([elem for elem in [_sess_str, _ply_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def SessionFilter(self) -> IDFilter:
        return self._session_filter

    @property
    def PlayerFilter(self) -> IDFilter:
        return self._player_filter

    @staticmethod
    def MakeSessionFilter(included_sessions:Optional[List[str] | Set[str]]=None) -> Filter:
        """Convenience function to set up a session filter for use with IDFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass:
        1. If `included_sessions` is set, and non-empty, use it to create a `SetFilter`.
        2. If `included_sessions` is not set, or is empty, create a `NoFilter`.


        :param included_sessions: _description_, defaults to None
        :type included_sessions: Optional[List[str]  |  Set[str]], optional
        :return: _description_
        :rtype: Filter
        """
        return IDFilterCollection._makeIDFilter(included_ids=included_sessions)

    @staticmethod
    def MakePlayerFilter(included_players:Optional[List[str] | Set[str]]=None) -> Filter:
        """Convenience function to set up a session filter for use with IDFilterCollection.

        This simply adds some type hinting and logic for picking the appropriate type of filter subclass:
        1. If `included_players` is set, and non-empty, use it to create a `SetFilter`.
        2. If `included_players` is not set, or is empty, create a `NoFilter`.


        :param included_players: _description_, defaults to None
        :type included_players: Optional[List[str]  |  Set[str]], optional
        :return: _description_
        :rtype: Filter
        """
        return IDFilterCollection._makeIDFilter(included_ids=included_players)

    @staticmethod
    def _makeIDFilter(included_ids:Optional[List[str] | Set[str]]=None) -> Filter:
        """Private function with the actual logic for creating an ID filter.

        Just exists because the logic for MakeSessionFilter and MakePlayerFilter is the same.
        If those ever diverge, this will be removed and they'll each use own specific logic.

        :param included_ids: _description_, defaults to None
        :type included_ids: Optional[List[str] | Set[str]], optional
        :return: _description_
        :rtype: Filter
        """
        if included_ids is not None:
            if len(included_ids) > 0:
                return SetFilter(mode=FilterMode.INCLUDE, set_elements=included_ids)
            else:
                return NoFilter()
        else:
            return NoFilter()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _asDict(self) -> Dict[str, Filter]:
        return {
            "session_id": self.SessionFilter,
            "player_id": self.PlayerFilter
        }
