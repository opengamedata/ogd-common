# standard imports
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Self

# ogd imports
from ogd.common.filters.Filter import Filter
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class DatasetSchema(Schema):
    """DatasetSchema struct

    TODO : Fill in description
    TODO : Add a _parseKey function, rather than having logic for that part sit naked in FromDict
    """
    _DEFAULT_DATE_MODIFIED = "UNKNOWN DATE"
    _DEFAULT_START_DATE = "UNKNOWN DATE"
    _DEFAULT_END_DATE = "UNKNOWN DATE"
    _DEFAULT_OGD_REVISION = "UNKNOWN REVISION"
    _DEFAULT_SESSION_COUNT = None
    _DEFAULT_PLAYER_COUNT = None
    _DEFAULT_FILTERS = {}
    _DEFAULT_RAW_FILE = None
    _DEFAULT_EVENTS_FILE = None
    _DEFAULT_EVENTS_TEMPLATE = None
    _DEFAULT_SESSIONS_FILE = None
    _DEFAULT_SESSIONS_TEMPLATE = None
    _DEFAULT_PLAYERS_FILE = None
    _DEFAULT_PLAYERS_TEMPLATE = None
    _DEFAULT_POPULATION_FILE = None
    _DEFAULT_POPULATION_TEMPLATE = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, key:DatasetKey,
                 game_id:Optional[str],
                 start_date:Optional[date|str],  end_date:Optional[date|str], date_modified:Optional[date|str], 
                 ogd_revision:Optional[str],     filters:Optional[Dict[str, str | Filter]],
                 session_ct:Optional[int],       player_ct:Optional[int],
                 raw_file:Optional[Path],  
                 events_file:Optional[Path],     events_template:Optional[Path],
                 sessions_file:Optional[Path],   sessions_template:Optional[Path],
                 players_file:Optional[Path],    players_template:Optional[Path],
                 population_file:Optional[Path], population_template:Optional[Path],
                 other_elements:Optional[Map]=None):
        """Constructor for the `DatasetSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "start_date": "01/01/2025",
            "end_date": "01/31/2025",
            "date_modified": "02/02/2025",
            "ogd_revision": "1234567",
            "filters" : {},
            "sessions": 1234,
            "population_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_population-features.zip",
            "population_template": "path/to/template",
            "players_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_player-features.zip",
            "players_template": "path/to/template",
            "sessions_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_session-features.zip",
            "sessions_template": "path/to/template",
            "events_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_events.zip",
            "events_template": "path/to/template",
            "all_events_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_all-events.zip",
            "all_events_template": "path/to/template
        },
        ```

        :param name: _description_
        :type name: str
        :param key: _description_
        :type key: DatasetKey
        :param date_modified: _description_
        :type date_modified: date | str
        :param start_date: _description_
        :type start_date: date | str
        :param end_date: _description_
        :type end_date: date | str
        :param ogd_revision: _description_
        :type ogd_revision: str
        :param session_ct: _description_
        :type session_ct: Optional[int]
        :param player_ct: _description_
        :type player_ct: Optional[int]
        :param raw_file: _description_
        :type raw_file: Optional[Path]
        :param events_file: _description_
        :type events_file: Optional[Path]
        :param events_template: _description_
        :type events_template: Optional[Path]
        :param sessions_file: _description_
        :type sessions_file: Optional[Path]
        :param sessions_template: _description_
        :type sessions_template: Optional[Path]
        :param players_file: _description_
        :type players_file: Optional[Path]
        :param players_template: _description_
        :type players_template: Optional[Path]
        :param population_file: _description_
        :type population_file: Optional[Path]
        :param population_template: _description_
        :type population_template: Optional[Path]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._key                 : DatasetKey     = key                 or DatasetKey.FromDateRange(game_id=game_id, start_date=start_date, end_date=end_date)
    # 1. Set dates
        self._date_modified       : date | str     = date_modified       or self._parseDateModified(unparsed_elements=unparsed_elements)
        self._start_date          : date | str     = start_date          or self._parseStartDate(unparsed_elements=unparsed_elements)
        self._end_date            : date | str     = end_date            or self._parseEndDate(unparsed_elements=unparsed_elements)
    # 2. Set metadata
        self._ogd_revision        : str            = ogd_revision        or self._parseOGDRevision(unparsed_elements=unparsed_elements)
        self._filters             : Dict[str, str | Filter] = filters    or self._parseFilters(unparsed_elements=unparsed_elements)
        self._session_ct          : Optional[int]  = session_ct          or self._parseSessionCount(unparsed_elements=unparsed_elements)
        self._player_ct           : Optional[int]  = player_ct           or self._parsePlayerCount(unparsed_elements=unparsed_elements)
    # 3. Set file/template paths
        self._raw_file            : Optional[Path] = raw_file            or self._parseRawFile(unparsed_elements=unparsed_elements)
        self._events_file         : Optional[Path] = events_file         or self._parseEventsFile(unparsed_elements=unparsed_elements)
        self._events_template     : Optional[Path] = events_template     or self._parseEventsTemplate(unparsed_elements=unparsed_elements)
        self._sessions_file       : Optional[Path] = sessions_file       or self._parseSessionsFile(unparsed_elements=unparsed_elements)
        self._sessions_template   : Optional[Path] = sessions_template   or self._parseSessionsTemplate(unparsed_elements=unparsed_elements)
        self._players_file        : Optional[Path] = players_file        or self._parsePlayersFile(unparsed_elements=unparsed_elements)
        self._players_template    : Optional[Path] = players_template    or self._parsePlayersTemplate(unparsed_elements=unparsed_elements)
        self._population_file     : Optional[Path] = population_file     or self._parsePopulationFile(unparsed_elements=unparsed_elements)
        self._population_template : Optional[Path] = population_template or self._parsePopulationTemplate(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    def __str__(self) -> str:
        return str(self.Key)

    # *** Properties ***

    @property
    def Key(self) -> DatasetKey:
        return self._key

    @property
    def DateModified(self) -> date | str:
        return self._date_modified
    @property
    def DateModifiedStr(self) -> str:
        ret_val : str
        if isinstance(self._date_modified, date):
            ret_val = self._date_modified.strftime("%m/%d/%Y")
        else:
            ret_val = self._date_modified
        return ret_val

    @property
    def StartDate(self) -> date | str:
        return self._start_date
    @StartDate.setter
    def StartDate(self, val:date | str):
        self._start_date = val

    @property
    def EndDate(self) -> date | str:
        return self._end_date
    @EndDate.setter
    def EndDate(self, val:date | str):
        self._end_date = val

    @property
    def OGDRevision(self) -> str:
        return self._ogd_revision

    @property
    def Filters(self) -> Dict[str, str | Filter]:
        return self._filters

    @property
    def SessionCount(self) -> Optional[int]:
        return self._session_ct
    @SessionCount.setter
    def SessionCount(self, val:Optional[int]):
        self._session_ct = val

    @property
    def PlayerCount(self) -> Optional[int]:
        return self._player_ct
    @PlayerCount.setter
    def PlayerCount(self, val:Optional[int]):
        self._player_ct = val

    @property
    def RawFile(self) -> Optional[Path]:
        return self._raw_file
    @property
    def EventsFile(self) -> Optional[Path]:
        return self._events_file
    @property
    def EventsTemplate(self) -> Optional[Path]:
        return self._events_template
    @property
    def SessionsFile(self) -> Optional[Path]:
        return self._sessions_file
    @property
    def SessionsTemplate(self) -> Optional[Path]:
        return self._sessions_template
    @property
    def PlayersFile(self) -> Optional[Path]:
        return self._players_file
    @property
    def PlayersTemplate(self) -> Optional[Path]:
        return self._players_template
    @property
    def PopulationFile(self) -> Optional[Path]:
        return self._population_file
    @property
    def PopulationTemplate(self) -> Optional[Path]:
        return self._population_template

    @property
    def FileSet(self) -> str:
        """
        The list of data files associated with the dataset.

        r -> Raw events file (no generated events)
        e -> All events file (with generated events)
        s -> Session features file
        p -> Player features file
        P -> Popoulation features file

        :return: The list of data files associated with the dataset.
        :rtype: str
        """
        _fset = [
           "r" if self.RawFile is not None else "",
           "e" if self.EventsFile is not None else "",
           "s" if self.SessionsFile is not None else "",
           "p" if self.PlayersFile is not None else "",
           "P" if self.PopulationFile is not None else ""
        ]
        return "".join(_fset)

    @property
    def TemplateSet(self) -> str:
        """
        The list of template files associated with the dataset.

        e -> Events template
        s -> Session features template
        p -> Player features template
        P -> Popoulation features template

        :return: The list of template files associated with the dataset.
        :rtype: str
        """
        _tset = [
           "e" if self.EventsTemplate is not None else "",
           "s" if self.SessionsTemplate is not None else "",
           "p" if self.PlayersTemplate is not None else "",
           "P" if self.PopulationTemplate is not None else ""
        ]
        return "".join(_tset)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = \
f"""{self.Name}: {self.PlayerCount} players across {self.SessionCount} sessions.  
Last modified {self.DateModified.strftime('%m/%d/%Y') if type(self.DateModified) == date else self.DateModified} with OGD v.{self.OGDRevision or 'UNKNOWN'}  
- Files: [{self.FileSet}]  
- Templates: [{self.TemplateSet}]"""
        return ret_val

    @property
    def AsMetadata(self) -> Dict[str, Optional[int | str | List | Dict]]:
        return {
            "game_id"      :self.Key.GameID,
            "dataset_id"   :str(self.Key),
            "ogd_revision" :self.OGDRevision,
            "filters"      :{name:str(filt) for name,filt in self.Filters.items()},
            "start_date"   :self.StartDate.strftime("%m/%d/%Y")    if isinstance(self.StartDate, date)    else self.StartDate,
            "end_date"     :self.EndDate.strftime("%m/%d/%Y")      if isinstance(self.EndDate, date)      else self.EndDate,
            "date_modified":self.DateModified.strftime("%m/%d/%Y") if isinstance(self.DateModified, date) else self.DateModified,
            "sessions"     :self.SessionCount,
            "population_file"     : str(self.PopulationFile),
            "population_template" : str(self.PopulationTemplate),
            "players_file"        : str(self.PlayersFile),
            "players_template"    : str(self.PlayersTemplate),
            "sessions_file"       : str(self.SessionsFile),
            "sessions_template"   : str(self.SessionsTemplate),
            "raw_file"            : str(self.RawFile),
            "events_template"     : str(self.EventsTemplate),
            "events_file"         : str(self.EventsFile),
            "all_events_template" : str(self.EventsTemplate)
        }

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DatasetSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetSchema
        """
        _key                 : DatasetKey     = DatasetKey(raw_key=name)

        return DatasetSchema(name=name, key=_key,
                             game_id=None,
                             date_modified=None, start_date=None, end_date=None,
                             ogd_revision=None, filters=None,
                             session_ct=None, player_ct=None,
                             raw_file=None,
                             events_file    =None, events_template    =None,
                             sessions_file  =None, sessions_template  =None,
                             players_file   =None, players_template   =None,
                             population_file=None, population_template=None,
                             other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "DatasetSchema":
        return DatasetSchema(
            name="DefaultDatasetSchema",
            key=DatasetKey.Default(),
            game_id             = DatasetKey._DEFAULT_GAME_ID,
            date_modified       = cls._DEFAULT_DATE_MODIFIED,
            start_date          = cls._DEFAULT_START_DATE,
            end_date            = cls._DEFAULT_END_DATE,
            ogd_revision        = cls._DEFAULT_OGD_REVISION,
            filters             = cls._DEFAULT_FILTERS,
            session_ct          = cls._DEFAULT_SESSION_COUNT,
            player_ct           = cls._DEFAULT_PLAYER_COUNT,
            raw_file            = cls._DEFAULT_RAW_FILE,
            events_file         = cls._DEFAULT_EVENTS_FILE,
            events_template     = cls._DEFAULT_EVENTS_TEMPLATE,
            sessions_file       = cls._DEFAULT_SESSIONS_FILE,
            sessions_template   = cls._DEFAULT_SESSIONS_TEMPLATE,
            players_file        = cls._DEFAULT_PLAYERS_FILE,
            players_template    = cls._DEFAULT_PLAYERS_TEMPLATE,
            population_file     = cls._DEFAULT_POPULATION_FILE,
            population_template = cls._DEFAULT_POPULATION_TEMPLATE,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def IsNewerThan(self, other:Optional[Self]) -> bool | None:
        """
        Check if `self` has a more recent "modified on" date than `other`.

        If `other` is None, returns True by default.  
        If both `self` and `other` are DatasetSchemas, but one (or both) is missing a "modified" date, returns None, because it is indeterminate. 

        :param other: The DatasetSchema to be compared with `self`.
        :type other: Optional[Self]
        :return: True if `self` has a more recent "modified" date than `other`, otherwise False. If one (or both) are missing "modified" date, then None. If `other` is None, True by default.
        :rtype: bool | None
        """
        if other == None:
            return True
        if isinstance(self.DateModified, date) and isinstance(other.DateModified, date):
            return self.DateModified > other.DateModified
        else:
            return None

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseDateModified(unparsed_elements:Map) -> date | str:
        """Function to obtain the modified date from a dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: date | str
        """
        ret_val : date | str
        date_modified = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["date_modified"],
            to_type=datetime,
            default_value=DatasetSchema._DEFAULT_DATE_MODIFIED,
            remove_target=True
        )
        if isinstance(date_modified, datetime):
            ret_val = date_modified.date()
        if isinstance(date_modified, date):
            ret_val = date_modified
        elif isinstance(date_modified, str):
            try:
                ret_val = datetime.strptime(date_modified, "%m/%d/%Y").date()
            except ValueError as err:
                ret_val = "UKNOWN DATE"
                Logger.Log(f"Invalid date_modified for dataset schema, expected a date, but got {date_modified}, resulting in error: {err}\nUsing {ret_val} instead")
        else:
            try:
                ret_val = datetime.strptime(str(date_modified), "%m/%d/%Y").date()
                Logger.Log(f"Dataset modified date was unexpected type {type(date_modified)}, defaulting to strptime(str(date_modified))={ret_val}.", logging.WARN)
            except ValueError as err:
                ret_val = "UKNOWN DATE"
                Logger.Log(f"Invalid date_modified for dataset schema, expected a date, but got {str(date_modified)}, resulting in error: {err}\nUsing {ret_val} instead.")
        return ret_val

    @staticmethod
    def _parseStartDate(unparsed_elements:Map) -> date | str:
        """Function to obtain the start date from a dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: date | str
        """
        ret_val : date | str
        start_date = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["start_date"],
            to_type=datetime,
            default_value=DatasetSchema._DEFAULT_START_DATE,
            remove_target=True
        )

        if isinstance(start_date, datetime):
            ret_val = start_date.date()
        if isinstance(start_date, date):
            ret_val = start_date
        elif isinstance(start_date, str):
            try:
                ret_val = datetime.strptime(start_date, "%m/%d/%Y").date()
            except ValueError as err:
                ret_val = "UKNOWN DATE"
                Logger.Log(f"Invalid start_date for dataset schema, expected a date, but got {start_date}, resulting in error: {err}\nUsing {ret_val} instead")
        else:
            try:
                ret_val = datetime.strptime(str(start_date), "%m/%d/%Y").date()
                Logger.Log(f"Dataset start date was unexpected type {type(start_date)}, defaulting to strptime(str(start_date))={ret_val}.", logging.WARN)
            except ValueError as err:
                ret_val = "UKNOWN DATE"
                Logger.Log(f"Invalid start_date for dataset schema, expected a date, but got {str(start_date)}, resulting in error: {err}\nUsing {ret_val} instead.")
        return ret_val

    @staticmethod
    def _parseEndDate(unparsed_elements:Map) -> date | str:
        """Function to obtain the end date from a dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: date | str
        """
        ret_val : date | str
        end_date = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["end_date"],
            to_type=datetime,
            default_value=DatasetSchema._DEFAULT_END_DATE,
            remove_target=True
        )

        if isinstance(end_date, datetime):
            ret_val = end_date.date()
        if isinstance(end_date, date):
            ret_val = end_date
        elif isinstance(end_date, str):
            try:
                ret_val = datetime.strptime(end_date, "%m/%d/%Y").date()
            except ValueError as err:
                ret_val = "UKNOWN DATE"
                Logger.Log(f"Invalid end_date for dataset schema, expected a date, but got {end_date}, resulting in error: {err}\nUsing {ret_val} instead")
        else:
            try:
                ret_val = datetime.strptime(str(end_date), "%m/%d/%Y").date()
                Logger.Log(f"Dataset end date was unexpected type {type(end_date)}, defaulting to strptime(str(end_date))={ret_val}.", logging.WARN)
            except ValueError as err:
                ret_val = "UKNOWN DATE"
                Logger.Log(f"Invalid end_date for dataset schema, expected a date, but got {str(end_date)}, resulting in error: {err}\nUsing {ret_val} instead")
        return ret_val

    @staticmethod
    def _parseOGDRevision(unparsed_elements:Map) -> str:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["ogd_revision"],
            to_type=str,
            default_value=DatasetSchema._DEFAULT_OGD_REVISION,
            remove_target=True
        )

    @staticmethod
    def _parseSessionCount(unparsed_elements:Map) -> Optional[int]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["sessions"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_SESSION_COUNT,
            remove_target=True
        )

    @staticmethod
    def _parsePlayerCount(unparsed_elements:Map) -> Optional[int]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["players"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_PLAYER_COUNT,
            remove_target=True
        )

    @staticmethod
    def _parseFilters(unparsed_elements:Map) -> Dict[str, Filter | str]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["filters"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_FILTERS,
            remove_target=True
        )

    @staticmethod
    def _parseRawFile(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        raw_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["raw_file"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_RAW_FILE,
            remove_target=True
        )
        if isinstance(raw_val, Path):
            ret_val = raw_val
        elif isinstance(raw_val, str):
            ret_val = Path(raw_val)
        else:
            ret_val = None
            Logger.Log(f"Invalid raw file path for dataset schema, expected a path, but got {str(raw_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseEventsFile(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        evt_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events_file"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_EVENTS_FILE,
            remove_target=True
        )
        if isinstance(evt_val, Path):
            ret_val = evt_val
        elif isinstance(evt_val, str):
            ret_val = Path(evt_val)
        else:
            ret_val = None
            Logger.Log(f"Invalid events file path for dataset schema, expected a path, but got {str(evt_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseSessionsFile(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        sess_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["sessions_file"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_SESSIONS_FILE,
            remove_target=True
        )
        if isinstance(sess_val, Path):
            ret_val = sess_val
        elif isinstance(sess_val, str):
            ret_val = Path(sess_val)
        else:
            ret_val = None
            Logger.Log(f"Invalid session file path for dataset schema, expected a path, but got {str(sess_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePlayersFile(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        play_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["players_file"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_PLAYERS_FILE,
            remove_target=True
        )
        if isinstance(play_val, Path):
            ret_val = play_val
        elif isinstance(play_val, str):
            ret_val = Path(play_val)
        else:
            ret_val = None
            Logger.Log(f"Invalid player file path for dataset schema, expected a path, but got {str(play_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePopulationFile(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        pop_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["population_file"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_POPULATION_FILE,
            remove_target=True
        )
        if isinstance(pop_val, Path):
            ret_val = pop_val
        elif isinstance(pop_val, str):
            ret_val = Path(pop_val)
        else:
            ret_val = None
            Logger.Log(f"Invalid population file path for dataset schema, expected a path, but got {str(pop_val)}, using {ret_val} instead")

        return ret_val


    @staticmethod
    def _parseEventsTemplate(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        events_tplate : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events_template"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_EVENTS_TEMPLATE,
            remove_target=True
        )
        if isinstance(events_tplate, Path):
            ret_val = events_tplate
        elif isinstance(events_tplate, str):
            ret_val = Path(events_tplate)
        else:
            ret_val = None
            Logger.Log(f"Invalid events template path for dataset schema, expected a path, but got {str(events_tplate)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseSessionsTemplate(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        sessions_tplate : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["sessions_template"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_SESSIONS_TEMPLATE,
            remove_target=True
        )
        if isinstance(sessions_tplate, Path):
            ret_val = sessions_tplate
        elif isinstance(sessions_tplate, str):
            ret_val = Path(sessions_tplate)
        else:
            ret_val = None
            Logger.Log(f"Invalid sessions template path for dataset schema, expected a path, but got {str(sessions_tplate)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePlayersTemplate(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        players_tplate : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["players_template"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_PLAYERS_TEMPLATE,
            remove_target=True
        )
        if isinstance(players_tplate, Path):
            ret_val = players_tplate
        elif isinstance(players_tplate, str):
            ret_val = Path(players_tplate)
        else:
            ret_val = None
            Logger.Log(f"Invalid player template path for dataset schema, expected a path, but got {str(players_tplate)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePopulationTemplate(unparsed_elements:Map) -> Optional[Path]:
        ret_val : Optional[Path]

        pop_tplate : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["population_template"],
            to_type=[Path, str],
            default_value=DatasetSchema._DEFAULT_POPULATION_TEMPLATE,
            remove_target=True
        )
        if isinstance(pop_tplate, Path):
            ret_val = pop_tplate
        elif isinstance(pop_tplate, str):
            ret_val = Path(pop_tplate)
        else:
            ret_val = None
            Logger.Log(f"Invalid population template path for dataset schema, expected a path, but got {str(pop_tplate)}, using {ret_val} instead")

        return ret_val

    # *** PRIVATE METHODS ***
