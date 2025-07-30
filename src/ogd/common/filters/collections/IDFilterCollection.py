## import standard libraries
from typing import List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode

class IDFilterCollection:
    type SessionFilterType = Optional[SetFilter[str]]
    type PlayerFilterType  = Optional[SetFilter[str]]

    """Dumb struct to hold filters for versioning information
    """
    def __init__(self, session_filter:SessionFilterType=None, player_filter:PlayerFilterType=None):
        self._session_filter = session_filter
        self._player_filter = player_filter

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        if self.SessionFilter or self.PlayerFilter:
            _sess_str = f"session(s) {self.SessionFilter}" if self.SessionFilter else None
            _ply_str = f"player(s) {self.PlayerFilter}" if self.PlayerFilter else None
            _ver_strs = ", ".join([elem for elem in [_sess_str, _ply_str] if elem is not None])
            ret_val = f"event filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.SessionFilter or self.PlayerFilter:
            _sess_str = f"session(s) {self.SessionFilter}" if self.SessionFilter else None
            _ply_str = f"player(s) {self.PlayerFilter}" if self.PlayerFilter else None
            _ver_strs = " ^ ".join([elem for elem in [_sess_str, _ply_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def SessionFilter(self) -> SessionFilterType:
        return self._session_filter
    @SessionFilter.setter
    def SessionFilter(self, included_sessions:Optional[SessionFilterType | List[str] | Set[str]]) -> None:
        if included_sessions is None:
            self._session_filter = None
        elif isinstance(included_sessions, SetFilter):
            self._session_filter = included_sessions
        elif isinstance(included_sessions, list) or isinstance(included_sessions, set):
            self._session_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(included_sessions))

    @property
    def PlayerFilter(self) -> PlayerFilterType:
        return self._player_filter
    @PlayerFilter.setter
    def PlayerFilter(self, included_players:Optional[PlayerFilterType | List[str] | Set[str]]) -> None:
        if included_players is None:
            self._player_filter = None
        elif isinstance(included_players, SetFilter):
            self._player_filter = included_players
        elif isinstance(included_players, list) or isinstance(included_players, set):
            self._player_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(included_players))

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
