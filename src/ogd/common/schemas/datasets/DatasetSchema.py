# standard imports
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Final, List, Optional, Self, overload

# ogd imports
from ogd.common.filters.Filter import Filter
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.schemas.events.EventSchema import EventSchema
from ogd.common.schemas.events.GameStateSchema import GameStateSchema
from ogd.common.schemas.events.DataElementSchema import DataElementSchema
from ogd.common.schemas.features.FeatureSchema import FeatureSchema
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map
from ogd.common.models.SemanticVersion import SemanticVersion

class DatasetSchema(Schema):
    """DatasetSchema struct

    TODO : Fill in description
    TODO : Add a _parseKey function, rather than having logic for that part sit naked in FromDict
    """
    _DEFAULT_GAME_ID             : Final[str]                     = "DEFAULT GAME"
    _DEFAULT_DATASET_ID          : Final[DatasetKey]              = DatasetKey.Default()
    # Population info
    _DEFAULT_FILTERS             : Final[Dict[str, str | Filter]] = {}
    _DEFAULT_SESSION_COUNT       : Final[int]                     = 0
    _DEFAULT_PLAYER_COUNT        : Final[int]                     = 0
    # Event info
    _DEFAULT_GAME_STATE          : Final[GameStateSchema]         = GameStateSchema.Default()
    _DEFAULT_EVENTS              : Final[List[EventSchema]]       = []
    # feature info
    _DEFAULT_FEATURES            : Final[List[FeatureSchema]]     = []
    # version info
    _DEFAULT_OGD_VERSION         : Final[str]                     = "UNKNOWN OGD VERSION"
    _DEFAULT_OGD_REVISION        : Final[str]                     = "UNKNOWN OGD REVISION"
    _DEFAULT_EVENT_VERSION       : Final[str]                     = "UNKNOWN EVENT SCHEMA VERSION"
    # output info
    _DEFAULT_FILES_LOCATION      : Final[Path]                    = Path("data/")
    _DEFAULT_RAW_FILE            : Final[bool]                    = False
    _DEFAULT_EVENTS_FILE         : Final[bool]                    = False
    _DEFAULT_COMB_FEATS_FILE     : Final[bool]                    = False
    _DEFAULT_SESSIONS_FILE       : Final[bool]                    = False
    _DEFAULT_PLAYERS_FILE        : Final[bool]                    = False
    _DEFAULT_POPULATION_FILE     : Final[bool]                    = False
    # deprecated, compatibility info
    _DEFAULT_DATE_MODIFIED       : Final[str]                     = "UNKNOWN DATE"
    _DEFAULT_START_DATE          : Final[str]                     = "UNKNOWN DATE"
    _DEFAULT_END_DATE            : Final[str]                     = "UNKNOWN DATE"

    # *** BUILT-INS & PROPERTIES ***

    # TODO : overload versions for individual parts of logging spec schema, vs. passing in a whole log spec schema
    def __init__(self, name:str, game_id:Optional[str],       dataset_id:DatasetKey,
                 filters:Optional[Dict[str, str | Filter]],   session_ct:Optional[int],           player_ct:Optional[int],
                 game_state:Optional[GameStateSchema],        events:Optional[List[EventSchema]], features:Optional[List[FeatureSchema]],
                 ogd_version:Optional[SemanticVersion | str], ogd_revision:Optional[str],         event_spec_version:Optional[SemanticVersion | str],
                 base_files_location:Optional[Path],
                 game_events_file:Optional[bool],             all_events_file:Optional[bool],     combined_feats_file:Optional[bool],
                 sessions_file:Optional[bool],                players_file:Optional[bool],        population_file:Optional[bool],
                 # deprecated, compatibility params
                 start_date:Optional[date|str],  end_date:Optional[date|str], date_modified:Optional[date|str], 
                 other_elements:Optional[Map]=None):
        """Constructor for the `DatasetSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "game_id" : "AQUALAB",
            "dataset_id" : "AQUALAB_20250101_to_20250131",
            "filters" : {},
            "session_count": 1234,
            "player_count": 123,
            "game_state" : {}
            "events" : []
            "features" : []
            "ogd_version": "1.2.3",
            "ogd_revision": "1234567",
            "event_spec_version": "1.0.0",
            "combined_features_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_combined-features.zip",
            "population_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_population-features.zip",
            "players_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_player-features.zip",
            "sessions_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_session-features.zip",
            "game_events_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_game-events.zip",
            "all_events_file": "path/to/GAME_NAME_20250101_to_20250131_1234567_all-events.zip",
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
        :param sessions_file: _description_
        :type sessions_file: Optional[Path]
        :param players_file: _description_
        :type players_file: Optional[Path]
        :param population_file: _description_
        :type population_file: Optional[Path]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._key                 : DatasetKey                  = dataset_id          if dataset_id          is not None else DatasetKey(game_id=game_id, from_date=start_date, to_date=end_date)
    # 1. Set population info
        self._session_ct          : Optional[int]               = session_ct          if session_ct          is not None else self._parseSessionCount(unparsed_elements=unparsed_elements, schema_name=name)
        self._player_ct           : Optional[int]               = player_ct           if player_ct           is not None else self._parsePlayerCount(unparsed_elements=unparsed_elements, schema_name=name)
    # 2. Set event info
        self._game_state          : Optional[GameStateSchema]   = game_state          if game_state          is not None else self._parseGameState(unparsed_elements=unparsed_elements, schema_name=name)
        self._events              : Optional[List[EventSchema]] = events              if events              is not None else self._parseEventList(unparsed_elements=unparsed_elements, schema_name=name)
    # 3. Set feature info
        self._features            : Optional[List[FeatureSchema]] = features          if features            is not None else self._parseFeatureList(unparsed_elements=unparsed_elements, schema_name=name)
    # 4. Set version info
        self._ogd_version         : SemanticVersion             = ogd_version         if ogd_version         is not None else self._parseOGDVersion(unparsed_elements=unparsed_elements, schema_name=name)
        self._ogd_revision        : str                         = ogd_revision        if ogd_revision        is not None else self._parseOGDRevision(unparsed_elements=unparsed_elements, schema_name=name)
        self._evt_spec_version    : SemanticVersion             = event_spec_version  if event_spec_version  is not None else self._parseEventSpecVersion(unparsed_elements=unparsed_elements, schema_name=name)
        self._filters             : Dict[str, str | Filter]     = filters             if filters             is not None else self._parseFilters(unparsed_elements=unparsed_elements, schema_name=name)
    # 5. Set output info
        self._base_files_location : Path                        = base_files_location if base_files_location is not None else self._parseBaseFileLocation(unparsed_elements=unparsed_elements, schema_name=name)
        self._all_events_file     : bool                        = all_events_file     if all_events_file     is not None else self._parseAllEventsFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._game_events_file    : bool                        = game_events_file    if game_events_file    is not None else self._parseGameEventsFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._all_features_file   : bool                        = combined_feats_file if combined_feats_file is not None else self._parseAllFeaturesFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._sessions_file       : bool                        = sessions_file       if sessions_file       is not None else self._parseSessionsFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._players_file        : bool                        = players_file        if players_file        is not None else self._parsePlayersFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._population_file     : bool                        = population_file     if population_file     is not None else self._parsePopulationFile(unparsed_elements=unparsed_elements, schema_name=name)
    # 6. Set deprecated/compatibility info
        self._date_modified       : date | str                  = date_modified       if date_modified       is not None else self._parseDateModified(unparsed_elements=unparsed_elements, schema_name=name)
        self._start_date          : date | str                  = start_date          if start_date          is not None else self._parseStartDate(unparsed_elements=unparsed_elements, schema_name=name)
        self._end_date            : date | str                  = end_date            if end_date            is not None else self._parseEndDate(unparsed_elements=unparsed_elements, schema_name=name)
        super().__init__(name=name, other_elements=other_elements)

    def __str__(self) -> str:
        return str(self.Key)

    # *** Properties ***

    @property
    def Key(self) -> DatasetKey:
        return self._key
    @property
    def DatasetID(self) -> str:
        return str(self.Key)

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
    def GameEventsFile(self) -> Optional[Path]:
        return self._base_files_location/ "Foo" if self._game_events_file else None
    @property
    def RawEventsFile(self) -> Optional[Path]:
        """Alias for GameEventsFile

        :return: _description_
        :rtype: Optional[Path]
        """
        return self.GameEventsFile

    @property
    def AllEventsFile(self) -> Optional[Path]:
        return self._base_files_location/ "Foo" if self._all_events_file else None
    @property
    def EventsFile(self) -> Optional[Path]:
        """Alias for AllEventsFile

        Since this is the main events file with all available events in it, we can just call it the "Events" file.

        :return: _description_
        :rtype: Optional[Path]
        """
        return self.AllEventsFile

    @property
    def FeaturesFile(self) -> Optional[Path]:
        """Alias for AllFeaturesFile
        
        Since this is the main base feature file, we can just call it the "Features" file.

        :return: _description_
        :rtype: Optional[Path]
        """
        return self.AllFeaturesFile
    @property
    def AllFeaturesFile(self) -> Optional[Path]:
        return self._base_files_location/ "Foo" if self._all_features_file else None
    
    @property
    def SessionsFile(self) -> Optional[Path]:
        return self._base_files_location/ "Foo" if self._sessions_file else None

    @property
    def PlayersFile(self) -> Optional[Path]:
        return self._base_files_location/ "Foo" if self._players_file else None

    @property
    def PopulationFile(self) -> Optional[Path]:
        return self._base_files_location/ "Foo" if self._population_file else None

    @property
    def FileSet(self) -> str:
        """
        The list of data files associated with the dataset.

        r -> Raw events file (no generated events)
        e -> All events file (with generated events)
        f -> All features file
        s -> Session features file
        p -> Player features file
        P -> Popoulation features file

        :return: The list of data files associated with the dataset.
        :rtype: str
        """
        _fset = [
           "r" if self.GameEventsFile is not None else "",
           "e" if self.AllEventsFile is not None else "",
           "f" if self.AllFeaturesFile is not None else "",
           "s" if self.SessionsFile is not None else "",
           "p" if self.PlayersFile is not None else "",
           "P" if self.PopulationFile is not None else ""
        ]
        return "".join(_fset)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = \
f"""{self.Name}: {self.PlayerCount} players across {self.SessionCount} sessions.  
Last modified {self.DateModified.strftime('%m/%d/%Y') if type(self.DateModified) == date else self.DateModified} with OGD v.{self.OGDRevision or 'UNKNOWN'}  
- Files: [{self.FileSet}]"""
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
            "all_features_file"     : str(self.AllFeaturesFile),
            "population_file"       : str(self.PopulationFile),
            "players_file"          : str(self.PlayersFile),
            "sessions_file"         : str(self.SessionsFile),
            "game_events_file"      : str(self.GameEventsFile),
            "all_events_file"       : str(self.AllEventsFile),
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
        _key                 : DatasetKey     = DatasetKey.FromString(raw_key=name)

        return DatasetSchema(
            name=name, dataset_id=_key,
            game_id=None,
            filters         =None, session_ct     =None, player_ct          =None,
            game_state      =None, events         =None, features           =None,
            ogd_version     =None, ogd_revision   =None, event_spec_version =None,
            base_files_location=None,
            game_events_file=None, all_events_file=None, combined_feats_file=None,
            sessions_file   =None, players_file   =None, population_file    =None,
            date_modified   =None, start_date     =None, end_date           =None,
            other_elements=unparsed_elements
        )

    @classmethod
    def Default(cls) -> "DatasetSchema":
        return DatasetSchema(
            name="DefaultDatasetSchema",
            dataset_id          = cls._DEFAULT_DATASET_ID,
            game_id             = cls._DEFAULT_GAME_ID,
            date_modified       = cls._DEFAULT_DATE_MODIFIED,
            start_date          = cls._DEFAULT_START_DATE,
            end_date            = cls._DEFAULT_END_DATE,
            filters             = cls._DEFAULT_FILTERS,
            session_ct          = cls._DEFAULT_SESSION_COUNT,
            player_ct           = cls._DEFAULT_PLAYER_COUNT,
            game_state          = cls._DEFAULT_GAME_STATE,
            events              = cls._DEFAULT_EVENTS,
            features            = cls._DEFAULT_FEATURES,
            ogd_version         = cls._DEFAULT_OGD_VERSION,
            ogd_revision        = cls._DEFAULT_OGD_REVISION,
            event_spec_version  = cls._DEFAULT_EVENT_VERSION,
            base_files_location = cls._DEFAULT_FILES_LOCATION,
            game_events_file    = cls._DEFAULT_RAW_FILE,
            all_events_file     = cls._DEFAULT_EVENTS_FILE,
            combined_feats_file = cls._DEFAULT_COMB_FEATS_FILE,
            sessions_file       = cls._DEFAULT_SESSIONS_FILE,
            players_file        = cls._DEFAULT_PLAYERS_FILE,
            population_file     = cls._DEFAULT_POPULATION_FILE,
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
    def _parseSessionCount(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[int]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["sessions"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_SESSION_COUNT,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parsePlayerCount(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[int]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["players"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_PLAYER_COUNT,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseGameState(unparsed_elements:Map, schema_name:Optional[str]=None) -> GameStateSchema:
        ret_val : GameStateSchema

        game_state = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_GAME_STATE,
            remove_target=True,
            schema_name=schema_name
        )
        ret_val = GameStateSchema.FromDict(name=f"{schema_name}GameState", unparsed_elements=game_state)

        return ret_val

    @staticmethod
    def _parseEvents(unparsed_elements:Map, schema_name:Optional[str]=None) -> GameStateSchema:
        ret_val : GameStateSchema

        game_state = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_GAME_STATE,
            remove_target=True,
            schema_name=schema_name
        )
        ret_val = GameStateSchema.FromDict(name=f"{schema_name}GameState", unparsed_elements=game_state)

        return ret_val

    @staticmethod
    def _parseFeatures(unparsed_elements:Map, schema_name:Optional[str]=None) -> GameStateSchema:
        ret_val : GameStateSchema

        game_state = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_GAME_STATE,
            remove_target=True,
            schema_name=schema_name
        )
        ret_val = GameStateSchema.FromDict(name=f"{schema_name}GameState", unparsed_elements=game_state)

        return ret_val

    @staticmethod
    def _parseDateModified(unparsed_elements:Map, schema_name:Optional[str]=None) -> date | str:
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
            remove_target=True,
            schema_name=schema_name
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
    def _parseStartDate(unparsed_elements:Map, schema_name:Optional[str]=None) -> date | str:
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
            remove_target=True,
            schema_name=schema_name
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
    def _parseEndDate(unparsed_elements:Map, schema_name:Optional[str]=None) -> date | str:
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
            remove_target=True,
            schema_name=schema_name
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
    def _parseOGDRevision(unparsed_elements:Map, schema_name:Optional[str]=None) -> str:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["ogd_revision"],
            to_type=str,
            default_value=DatasetSchema._DEFAULT_OGD_REVISION,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseFilters(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, Filter | str]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["filters"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_FILTERS,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseGameEventsFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[Path]:
        ret_val : Optional[Path]

        raw_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_RAW_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_val, Path) or raw_val is None:
            ret_val = raw_val
        else:
            ret_val = None
            Logger.Log(f"Invalid raw file path for dataset schema, expected a path, but got {str(raw_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseAllEventsFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[Path]:
        ret_val : Optional[Path]

        evt_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["all_events_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_EVENTS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(evt_val, Path) or evt_val is None:
            ret_val = evt_val
        else:
            ret_val = None
            Logger.Log(f"Invalid events file path for dataset schema, expected a path, but got {str(evt_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseAllFeaturesFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[Path]:
        ret_val : Optional[Path]

        feats_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["all_features_file", "features_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_COMB_FEATS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(feats_val, Path) or feats_val is None:
            ret_val = feats_val
        else:
            ret_val = None
            Logger.Log(f"Invalid all-features file path for dataset schema, expected a path, but got {str(feats_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseSessionsFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[Path]:
        ret_val : Optional[Path]

        sess_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["sessions_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_SESSIONS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(sess_val, Path) or sess_val is None:
            ret_val = sess_val
        else:
            ret_val = None
            Logger.Log(f"Invalid session file path for dataset schema, expected a path, but got {str(sess_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePlayersFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[Path]:
        ret_val : Optional[Path]

        play_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["players_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_PLAYERS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(play_val, Path) or play_val is None:
            ret_val = play_val
        else:
            ret_val = None
            Logger.Log(f"Invalid player file path for dataset schema, expected a path, but got {str(play_val)}, using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePopulationFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[Path]:
        ret_val : Optional[Path]

        pop_val : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["population_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_POPULATION_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(pop_val, Path) or pop_val is None:
            ret_val = pop_val
        else:
            ret_val = None
            Logger.Log(f"Invalid population file path for dataset schema, expected a path, but got {str(pop_val)}, using {ret_val} instead")

        return ret_val

    # *** PRIVATE METHODS ***
