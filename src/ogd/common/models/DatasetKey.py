# standard imports
from calendar import monthrange
from datetime import date, datetime
from pathlib import Path
from typing import Final, List, Optional, Tuple

from dateutil.parser import parse as dateparse

class DatasetKey:
    """
    DatasetKey dumb struct.

    TODO : Rework this to be more like other schemas.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_GAME_ID   : Final[str] = "UNKOWN_GAME"
    _DEFAULT_DATE_FROM : Final[date] = date(year=2000, month=1, day=1)
    _DEFAULT_DATE_TO   : Final[date] = date(year=2000, month=1, day=31)

    """Simple little class to make logic with dataset keys easier
    """
    def __init__(self, game_id:str,
                 full_month:Optional[str | Tuple[int, int]]=None,
                 from_date:Optional[date]=None, to_date:Optional[date]=None,
                 player_id:Optional[str]=None, player_id_file:Optional[str|Path]=None,
                 session_id:Optional[str]=None, session_id_file:Optional[str|Path]=None
    ):
        self._game_id      : str = game_id or DatasetKey._DEFAULT_GAME_ID
        if not any(x is not None for x in [full_month, from_date, to_date, player_id, player_id_file, session_id, session_id_file]):
            raise ValueError("Attempted to create DatasetKey without specifying dates or a player or a session identifier!")
        else:
            self._from_date : Optional[date]
            self._to_date   : Optional[date]
            if full_month:
                if isinstance(full_month, str):
                    month_start = dateparse(timestr=full_month, default=datetime.min)
                    _, month_end = monthrange(year=month_start.year, month=month_start.month)
                    self._from_date = month_start.date()
                    self._to_date   = month_start.replace(day=month_end).date()
            else:
                self._from_date  = from_date
                self._to_date    = to_date
            self._player_id       : Optional[str]  = player_id
            self._player_id_file  : Optional[str]  = player_id_file.name if isinstance(player_id_file, Path) else player_id_file
            self._session_id      : Optional[str]  = session_id
            self._session_id_file : Optional[str]  = session_id_file.name if isinstance(session_id_file, Path) else session_id_file

    def __str__(self):
        """Returns formatted string for the dataset key, with the form "GAME_ID_<from_ID>_<YYYYMMDD_to_YYYYMMDD>"

        The formatting works as follows:
        1. `game_id` always comes first
        2. If a date range was given, it always appears at the end in form `YYYYMMDD_to_YYYYMMDD`, where the first part is the earliest day, the later part is the last day.
        3. If session/player IDs were given, the most-specific such ID appears after the `game_id`  
            a. A session ID is always more specific than a player ID  
            b. A single ID is always more specific than a file.  
            * Note that in general, the system should never allow you to specify multiple IDs,
            e.g. you should not be able to ever request a player ID files and a specific individual session ID.
            Should any such issue arrive, however, it will be resolved with the logic above.  

        :return: _description_
        :rtype: _type_
        """
        date_clause = f"{self._from_date}_to_{self._to_date}" if self._from_date and self._to_date else ""
        id_clause = f"from_{self._session_id or self._session_id_file or self._player_id or self._player_id_file}"
        return "_".join([self._game_id, id_clause, date_clause])
    
    @property
    def IsValid(self) -> bool:
        range_elements = [
            self._from_date, self._to_date,
            self._player_id, self._player_id_file,
            self._session_id, self._session_id_file
        ]
        return any(elem is not None for elem in range_elements)
    @property
    def GameID(self) -> str:
        return self._game_id
    @property
    def DateFrom(self) -> Optional[date]:
        return self._from_date
    @property
    def DateTo(self) -> Optional[date]:
        return self._to_date

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetKey":
        return DatasetKey(
            game_id=cls._DEFAULT_GAME_ID,
            from_date=cls._DEFAULT_DATE_FROM,
            to_date=cls._DEFAULT_DATE_TO
        )

    @staticmethod
    def FromString(raw_key:str):
        """Parse a dataset key from string.

        For now, it always assumes a string of the form "GAME_ID_..._YYYYMMDD_to_YYYYMMDD",
        where the "..." indicates the GAME_ID could have arbitrarily many "_"-separated pieces.  
        In the future, we hope to support the full range of possible valid DatasetKey formats.

        .. TODO : Support strings of the form "GAME_ID_..._from_session_id"  
        .. TODO : Support strings of the form "GAME_ID_..._from_session_id_file_..._YYYYMMDD_to_YYYYMMDD"  

        :param raw_key: _description_
        :type raw_key: str
        :return: _description_
        :rtype: _type_
        """
    # 1. Get Game ID from key
        pieces = raw_key.split("_")
        _game_id = "_".join(pieces[:-3]) if len(pieces) >= 4 else "INVALID DATASET KEY"
    # 2. Get Dates from key
        # If this _dataset_key matches the expected format,
        # i.e. split is: ["GAME", "ID", "PARTS",..., "YYYYMMDD", "to", "YYYYMMDD"]
        # Technically, the dates aren't required, and we could have a player ID instead.
        # In that case, we just don't have dates built into the Key.
        # File API should be prepared to account for this.
        _from_date : date = DatasetKey._DEFAULT_DATE_FROM
        _to_date : date = DatasetKey._DEFAULT_DATE_TO
        if len(pieces[-3]) == 8:
            _from_date = dateparse(pieces[3]).date()
        if len(pieces[-1]) == 8:
            _to_date = dateparse(pieces[-1]).date()
        return DatasetKey(game_id=_game_id, from_date=_from_date, to_date=_to_date)

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
