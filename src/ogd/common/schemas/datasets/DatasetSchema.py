# standard imports
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, Final, Optional, Self

# ogd imports
from ogd.common.filters.Filter import Filter
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.configs.locations.LocationConfig import LocationConfig
from ogd.common.configs.locations.FileLocationConfig import FileLocationConfig
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.schemas.events.EventSchema import EventSchema
from ogd.common.schemas.events.GameStateSchema import GameStateSchema
from ogd.common.schemas.features.FeatureSchema import FeatureSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import conversions, JSONMap, Map
from ogd.common.models.SemanticVersion import SemanticVersion

type DatasetManifest = DatasetSchema

class DatasetSchema(Schema):
    """DatasetSchema struct

    TODO : Fill in description
    TODO : Add a _parseKey function, rather than having logic for that part sit naked in FromDict
    TODO : Deal with how to handle game ID, particularly since we don't typically include the game ID in dictionaries when using FromDict
    """
    _DEFAULT_GAME_ID             : Final[None]                    = None
    _DEFAULT_DATASET_ID          : Final[DatasetKey]              = DatasetKey.Default()
    # Population info
    _DEFAULT_FILTERS             : Final[Dict[str, str | Filter]] = {}
    _DEFAULT_SESSION_COUNT       : Final[int]                     = 0
    _DEFAULT_PLAYER_COUNT        : Final[None]                    = None
    # Event info
    _DEFAULT_GAME_STATE          : Final[GameStateSchema]         = GameStateSchema.Default()
    _DEFAULT_EVENTS              : Final[Dict[str, EventSchema]]  = {}
    # feature info
    _DEFAULT_FEATURES            : Final[Dict[str, FeatureSchema]] = {}
    # version info
    _DEFAULT_OGD_VERSION         : Final[SemanticVersion]         = SemanticVersion.FromString("UNKNOWN OGD VERSION")
    _DEFAULT_OGD_REVISION        : Final[str]                     = "UNKNOWN OGD REVISION"
    _DEFAULT_EVENT_VERSION       : Final[SemanticVersion]         = SemanticVersion(0, 0, 1)
    # output info
    _DEFAULT_FILES_LOCATION      : Final[DirectoryLocationConfig] = DirectoryLocationConfig(name="Default File Location", folder_path=Path("data/"))
    _DEFAULT_RAW_FILE            : Final[None]                    = None
    _DEFAULT_EVENTS_FILE         : Final[None]                    = None
    _DEFAULT_COMB_FEATS_FILE     : Final[None]                    = None
    _DEFAULT_SESSIONS_FILE       : Final[None]                    = None
    _DEFAULT_PLAYERS_FILE        : Final[None]                    = None
    _DEFAULT_POPULATION_FILE     : Final[None]                    = None
    # deprecated, compatibility info
    _DEFAULT_DATE_MODIFIED       : Final[None]                     = None
    _DEFAULT_START_DATE          : Final[None]                     = None
    _DEFAULT_END_DATE            : Final[None]                     = None

    # *** BUILT-INS & PROPERTIES ***

    # TODO : overload versions for individual parts of logging spec schema, vs. passing in a whole log spec schema
    def __init__(self, name:str, game_id:Optional[str],       dataset_id:Optional[DatasetKey],
                 filters:Optional[Dict[str, str | Filter]],   session_ct:Optional[int],                 player_ct:Optional[int],
                 game_state:Optional[GameStateSchema | Dict], events:Optional[Dict[str, EventSchema]],  features:Optional[Dict[str, FeatureSchema]],
                 ogd_version:Optional[SemanticVersion | str], ogd_revision:Optional[str],               event_spec_version:Optional[SemanticVersion | str],
                 base_files_location:Optional[LocationConfig],
                 game_events_file:Optional[LocationConfig],   all_events_file:Optional[LocationConfig], combined_feats_file:Optional[LocationConfig],
                 sessions_file:Optional[LocationConfig],      players_file:Optional[LocationConfig],    population_file:Optional[LocationConfig],
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

    # 1. Set population info
        self._session_ct          : Optional[int]                    = self._getSessionCount(raw_val=session_ct, unparsed_elements=unparsed_elements, schema_name=name)
        self._player_ct           : Optional[int]                    = self._getPlayerCount(raw_val=player_ct, unparsed_elements=unparsed_elements, schema_name=name)
        self._filters             : Dict[str, str | Filter]          = self._getFilters(raw_val=filters, unparsed_elements=unparsed_elements, schema_name=name)
    # 2. Set event info
        self._game_state          : Optional[GameStateSchema]        = self._getGameState(raw_val=game_state, unparsed_elements=unparsed_elements, schema_name=name)
        self._events              : Optional[Dict[str, EventSchema]] = self._getEvents(raw_val=events, unparsed_elements=unparsed_elements, schema_name=name)
    # 3. Set feature info
        self._features            : Optional[Dict[str, FeatureSchema]] = self._getFeatures(raw_val=features, unparsed_elements=unparsed_elements, schema_name=name)
    # 4. Set version info
        self._ogd_version         : SemanticVersion                  = self._getOGDVersion(raw_val=ogd_version, unparsed_elements=unparsed_elements, schema_name=name)
        self._ogd_revision        : str                              = self._getOGDRevision(raw_val=ogd_revision, unparsed_elements=unparsed_elements, schema_name=name)
        self._evt_spec_version    : SemanticVersion                  = self._getEventSpecVersion(raw_val=event_spec_version, unparsed_elements=unparsed_elements, schema_name=name)
    # 5. Set output info
        self._base_files_location : Optional[LocationConfig]         = self._getBaseFileLocation(raw_val=base_files_location, unparsed_elements=unparsed_elements, schema_name=name)
        self._all_events_file     : Optional[LocationConfig]         = self._getAllEventsFile(raw_val=all_events_file, unparsed_elements=unparsed_elements, schema_name=name)
        self._game_events_file    : Optional[LocationConfig]         = self._getGameEventsFile(raw_val=game_events_file, unparsed_elements=unparsed_elements, schema_name=name)
        self._all_features_file   : Optional[LocationConfig]         = self._getAllFeaturesFile(raw_val=combined_feats_file, unparsed_elements=unparsed_elements, schema_name=name)
        self._sessions_file       : Optional[LocationConfig]         = self._getSessionsFile(raw_val=sessions_file, unparsed_elements=unparsed_elements, schema_name=name)
        self._players_file        : Optional[LocationConfig]         = self._getPlayersFile(raw_val=players_file, unparsed_elements=unparsed_elements, schema_name=name)
        self._population_file     : Optional[LocationConfig]         = self._getPopulationFile(raw_val=population_file, unparsed_elements=unparsed_elements, schema_name=name)
    # 6. Set deprecated/compatibility info
        self._date_modified       : Optional[date]                   = self._getDateModified(raw_val=date_modified, unparsed_elements=unparsed_elements, schema_name=name)
        self._start_date          : Optional[date]                   = self._getStartDate(raw_val=start_date, unparsed_elements=unparsed_elements, schema_name=name)
        self._end_date            : Optional[date]                   = self._getEndDate(raw_val=end_date, unparsed_elements=unparsed_elements, schema_name=name)
    # 7. Finally, get key
        # a. If there is a dataset_id given directly, it goes in as the 'raw_value', which has top priority.
        # b. If there is a dataset_id in the dict, it'll be parsed.
        # c. If there is a game_id, and start and end dates, they are used to create an override of the class default, and will be used.
        # d. If all else fails, we'll parse a DatasetKey from the schema name in the _getDatasetID function.
        # e. If somehow we don't even have that, backstop is the class default dataset ID.
        _game_id                  : Optional[str]                    = self._getGameID(raw_val=game_id, unparsed_elements=unparsed_elements)
        _default_id               : Optional[DatasetKey]             = DatasetKey(game_id=_game_id, from_date=self._start_date, to_date=self._end_date) if _game_id and self._start_date and self._end_date else None
        self._key                 : DatasetKey                       = self._getDatasetID(raw_val=dataset_id, unparsed_elements=unparsed_elements, schema_name=name, default_override=_default_id)

        leftovers = {key:val for key,val in unparsed_elements.items() if key not in {"population", "versioning", "output"}}
        super().__init__(name=name, other_elements=leftovers)

    def __str__(self) -> str:
        return str(self.Key)

    # *** Properties ***

    @property
    def Key(self) -> DatasetKey:
        return self._key
    @property
    def DatasetID(self) -> str:
        return str(self.Key)

    # 1. Get/set population info

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
    def Filters(self) -> Dict[str, str | Filter]:
        return self._filters

    # 2. Get event info

    @property
    def GameState(self) -> Optional[GameStateSchema]:
        return self._game_state

    @property
    def Events(self) -> Optional[Dict[str, EventSchema]]:
        return self._events

    # 3. Get feature info

    @property
    def Features(self) -> Optional[Dict[str, FeatureSchema]]:
        return self._features
    
    # 4. Get version info

    @property
    def OGDVersion(self) -> SemanticVersion:
        return self._ogd_version

    @property
    def OGDRevision(self) -> str:
        return self._ogd_revision

    @property
    def EventSpecificationVersion(self) -> SemanticVersion:
        return self._evt_spec_version

    # 5. Get output info

    # TODO : all the location schema stuff is screwy; for now types assume general LocationConfig, since in the future we could use paths or URLS.
    # Meanwhile, all the literal implementation details assume we're using paths, i.e. FileLocationConfigs.

    @property
    def BaseFileLocation(self) -> Optional[LocationConfig]:
        return self._base_files_location
    @BaseFileLocation.setter
    def BaseFileLocation(self, new_loc:Optional[LocationConfig]):
        self._base_files_location = new_loc

    def GameEventsFile(self, relative:bool=False) -> Optional[str]:
        ret_val : Optional[str] = None
        if self._game_events_file is not None:
            if not relative and self._base_files_location:
                ret_val = self._base_files_location / self._game_events_file
            else: # either relative was requested, or there is no base to construct an absolute path:
                ret_val = self._game_events_file.Location
        return ret_val
    def RawEventsFile(self, relative:bool=False) -> Optional[str]:
        """Alias for GameEventsFile

        :return: _description_
        :rtype: Optional[Path]
        """
        return self.GameEventsFile(relative=relative)
    @property
    def HasGameEventsFile(self) -> bool:
        return self.GameEventsFile() is not None

    def AllEventsFile(self, relative:bool=False) -> Optional[str]:
        ret_val : Optional[str] = None
        if self._all_events_file is not None:
            if not relative and self._base_files_location:
                ret_val = self._base_files_location / self._all_events_file
            else: # either relative was requested, or there is no base to construct an absolute path:
                ret_val = self._all_events_file.Location
        return ret_val
    def EventsFile(self, relative:bool=False) -> Optional[str]:
        """Alias for AllEventsFile

        Since this is the main events file with all available events in it, we can just call it the "Events" file.

        :return: _description_
        :rtype: Optional[Path]
        """
        return self.AllEventsFile(relative=relative)
    @property
    def HasAllEventsFile(self) -> bool:
        return self.AllEventsFile() is not None

    def CombinedFeaturesFile(self, relative:bool=False) -> Optional[str]:
        ret_val : Optional[str] = None
        if self._all_features_file is not None:
            if not relative and self._base_files_location:
                ret_val = self._base_files_location / self._all_features_file
            else: # either relative was requested, or there is no base to construct an absolute path:
                ret_val = self._all_features_file.Location
        return ret_val
    def FeaturesFile(self, relative:bool=False) -> Optional[str]:
        """Alias for AllFeaturesFile
        
        Since this is the main base feature file, we can just call it the "Features" file.

        :return: _description_
        :rtype: Optional[Path]
        """
        return self.CombinedFeaturesFile(relative=relative)
    @property
    def HasCombinedFeaturesFile(self) -> bool:
        return self.CombinedFeaturesFile() is not None
    
    def SessionsFile(self, relative:bool=False) -> Optional[str]:
        ret_val : Optional[str] = None
        if self._sessions_file is not None:
            if not relative and self._base_files_location:
                ret_val = self._base_files_location / self._sessions_file
            else: # either relative was requested, or there is no base to construct an absolute path:
                ret_val = self._sessions_file.Location
        return ret_val
    @property
    def HasSessionsFile(self) -> bool:
        return self.SessionsFile() is not None

    def PlayersFile(self, relative:bool=False) -> Optional[str]:
        ret_val : Optional[str] = None
        if self._players_file is not None:
            if not relative and self._base_files_location:
                ret_val = self._base_files_location / self._players_file
            else: # either relative was requested, or there is no base to construct an absolute path:
                ret_val = self._players_file.Location
        return ret_val
    @property
    def HasPlayersFile(self) -> bool:
        return self.PlayersFile() is not None

    def PopulationFile(self, relative:bool=False) -> Optional[str]:
        ret_val : Optional[str] = None
        if self._population_file is not None:
            if not relative and self._base_files_location:
                ret_val = self._base_files_location / self._population_file
            else: # either relative was requested, or there is no base to construct an absolute path:
                ret_val = self._population_file.Location
        return ret_val
    @property
    def HasPopulationFile(self) -> bool:
        return self.PopulationFile() is not None

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
           "f" if self.CombinedFeaturesFile is not None else "",
           "s" if self.SessionsFile is not None else "",
           "p" if self.PlayersFile is not None else "",
           "P" if self.PopulationFile is not None else ""
        ]
        return "".join(_fset)

    # 6. Get deprecated/compatibility info

    @property
    def DateModified(self) -> Optional[date]:
        return self._date_modified
    @property
    def DateModifiedStr(self) -> str:
        ret_val : str
        if isinstance(self._date_modified, date):
            ret_val = self._date_modified.strftime("%m/%d/%Y")
        else:
            ret_val = "UNKNOWN DATE"
        return ret_val

    @property
    def StartDate(self) -> Optional[date]:
        return self._start_date
    @property
    def StartDateStr(self) -> str:
        ret_val : str
        if isinstance(self._start_date, date):
            ret_val = self._start_date.strftime("%m/%d/%Y")
        else:
            ret_val = "UNKNOWN DATE"
        return ret_val
    @StartDate.setter
    def StartDate(self, val:date | str):
        self._start_date = self._getStartDate(raw_val=val, unparsed_elements={})

    @property
    def EndDate(self) -> Optional[date]:
        return self._end_date
    @property
    def EndDateStr(self) -> str:
        ret_val : str
        if isinstance(self._end_date, date):
            ret_val = self._end_date.strftime("%m/%d/%Y")
        else:
            ret_val = "UNKNOWN DATE"
        return ret_val
    @EndDate.setter
    def EndDate(self, val:date | str):
        self._end_date = self._getEndDate(raw_val=val, unparsed_elements={})

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = \
f"""{self.Name}: {self.PlayerCount} players across {self.SessionCount} sessions.  
Last modified {self.DateModified.strftime('%m/%d/%Y') if type(self.DateModified) == date else self.DateModified} with OGD v.{self.OGDRevision or 'UNKNOWN'}  
- Files: [{self.FileSet}]"""
        return ret_val

    @property
    def AsMetadata(self) -> JSONMap:
        return self.AsDict

    @property
    def AsDict(self) -> JSONMap:
        return {
            "game_id"            : self.Key.GameID,
            "dataset_id"         : str(self.Key),
            "population": {
                "session_count"      : self.SessionCount,
                "player_count"       : self.PlayerCount,
                "filters"            : {name:str(filt) for name,filt in self.Filters.items()},
            },
            "game_state"         : self.GameState.AsDict if self.GameState else None,
            "events"             : { key : event.AsDict for key,event in self.Events.items() } if self.Events else None,
            "features"           : { key : feature.AsDict for key,feature in self.Features.items() } if self.Features else None,
            "versioning": {
                "ogd_version"        : str(self.OGDVersion),
                "ogd_revision"       : self.OGDRevision,
                "event_spec_version" : str(self.EventSpecificationVersion),
            },
            # output info
            "output": {
                # "base_file_location" : str(self._base_files_location),
                "all_events_file"    : self.AllEventsFile(relative=True),
                "game_events_file"   : self.GameEventsFile(relative=True),
                "all_features_file"  : self.CombinedFeaturesFile(relative=True),
                "sessions_file"      : self.SessionsFile(relative=True),
                "players_file"       : self.PlayersFile(relative=True),
                "population_file"    : self.PopulationFile(relative=True)
            },
            # deprecated/compatibility info
            "date_modified"      : self.DateModified.strftime("%m/%d/%Y") if isinstance(self.DateModified, date) else self.DateModified,
            "start_date"         : self.StartDate.strftime("%m/%d/%Y")    if isinstance(self.StartDate, date)    else self.StartDate,
            "end_date"           : self.EndDate.strftime("%m/%d/%Y")      if isinstance(self.EndDate, date)      else self.EndDate,
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
        # _key                 : DatasetKey     = DatasetKey.FromString(raw_key=name)

        return DatasetSchema(
            name=name, dataset_id=None,
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

    #region *** PRIVATE STATICS ***

    @staticmethod
    def _getGameID(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[str]:

        return DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["game_id"],
            to_type=str,
            default_value=DatasetSchema._DEFAULT_GAME_ID,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )

    @staticmethod
    def _getDatasetID(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None, default_override:Optional[DatasetKey]=None) -> DatasetKey:
        ret_val : DatasetKey

        default_val = default_override if default_override else DatasetKey.FromString(schema_name) if schema_name else DatasetSchema._DEFAULT_DATASET_ID

        raw_id : DatasetKey | str | dict = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["dataset_id", "dataset_key"],
            to_type=[DatasetKey, str],
            default_value=default_val,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match raw_id:
            case DatasetKey():
                ret_val = raw_id
            case str():
                ret_val = DatasetKey.FromString(raw_key=raw_id)
            case _:
                ret_val = DatasetSchema._DEFAULT_DATASET_ID
        
        return ret_val

        #region Parse population info
    @staticmethod
    def _getSessionCount(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[int]:
        # look for session count in the population section, if it exists.
        population_elements = unparsed_elements.get("population", unparsed_elements)

        return DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=population_elements,
            valid_keys=["sessions", "session_count"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_SESSION_COUNT,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True # This should stop being optional once datasets are re-run with ogd-core 1.0
        )

    @staticmethod
    def _getPlayerCount(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[int]:
        # look for player count in the population section, if it exists.
        population_elements = unparsed_elements.get("population", unparsed_elements)

        return DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=population_elements,
            valid_keys=["players", "player_count"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_PLAYER_COUNT,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True # This should stop being optional once datasets are re-run with ogd-core 1.0
        )

    @staticmethod
    def _getFilters(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, Filter | str]:
        # look for filters in the population section, if it exists.
        population_elements = unparsed_elements.get("population", unparsed_elements)

        return DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=population_elements,
            valid_keys=["filters"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_FILTERS,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True # This should stop being optional once datasets are re-run with ogd-core 1.0
        )
        #endregion

        #region Parse event info
    @staticmethod
    def _getGameState(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> GameStateSchema:
        ret_val : GameStateSchema

        game_state = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=[GameStateSchema, dict],
            default_value=DatasetSchema._DEFAULT_GAME_STATE,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match game_state:
            case GameStateSchema():
                ret_val = game_state
            case dict():
                ret_val = GameStateSchema.FromDict(name=f"{schema_name}GameState", unparsed_elements=game_state)
            case _:
                ret_val = DatasetSchema._DEFAULT_GAME_STATE
                Logger.Log(f"In DatasetSchema, raw game state element was unexpected type {type(game_state)}, defaulting to {ret_val}.", logging.WARN)

        return ret_val

    @staticmethod
    def _getEvents(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, EventSchema]:
        ret_val : Dict[str, EventSchema]

        def _getEvent(event_name:Optional[str], event:Any) -> EventSchema:
            ret_val : EventSchema
            match event:
                case EventSchema():
                    ret_val = event
                case dict():
                    ret_val = EventSchema.FromDict(
                        name=event_name or unparsed_elements.get("event_name", "UNKNOWN EVENT"),
                        unparsed_elements=event
                    )
                case _:
                    raise TypeError(f"Event element was incompatible type {type(event)}!")
            return ret_val

        raw_events = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["events"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_EVENTS,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        ret_val = {
            event_name : _getEvent(event_name=event_name, event=raw_event)
            for event_name, raw_event in raw_events.items()
        }

        return ret_val
        #endregion

        #region Parse feature info
    @staticmethod
    def _getFeatures(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, FeatureSchema]:
        ret_val : Dict[str, FeatureSchema]

        def _getFeature(feat_name:Optional[str], feature:Any) -> FeatureSchema:
            ret_val : FeatureSchema
            match feature:
                case FeatureSchema():
                    ret_val = feature
                case dict():
                    ret_val = FeatureSchema.FromDict(
                        name=feat_name or unparsed_elements.get("feature_name", FeatureSchema._DEFAULT_FEAT_NAME),
                        unparsed_elements=feature
                    )
                case _:
                    raise TypeError(f"Feature element was incompatible type {type(feature)}!")
            return ret_val

        raw_features = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["features"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_FEATURES,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        ret_val = {
            feat_name : _getFeature(feat_name=feat_name, feature=raw_feat)
            for feat_name, raw_feat in raw_features.items()
        }

        return ret_val
        #endregion

        #region Parse version info

    @staticmethod
    def _getOGDVersion(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> SemanticVersion:
        ret_val : SemanticVersion

        # 1. Get a raw 'version' value to work with.

        # look for OGD version in the versioning section, if it exists.
        versioning_elements = unparsed_elements.get("versioning", unparsed_elements)

        raw_version : SemanticVersion | str = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=versioning_elements,
            valid_keys=["ogd_version"],
            to_type=[SemanticVersion, str],
            default_value=DatasetSchema._DEFAULT_OGD_VERSION,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True # This should stop being optional once datasets are re-run with ogd-core 1.0
        )
        # 2. Turn the raw version into a parsed-out SemanticVersion
        match raw_version:
            case SemanticVersion():
                ret_val = raw_version
            case str():
                ret_val = SemanticVersion.FromString(semver=raw_version, verbose=False)
            case _:
                Logger.Log(f"In DatasetSchema, raw OGD version was unexpected type {type(raw_version)}, using SemanticVersion.FromString(str(raw_version))", logging.WARNING)
                ret_val = SemanticVersion.FromString(str(raw_version))

        return ret_val

    @staticmethod
    def _getOGDRevision(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> str:
        # look for OGD revision in the versioning section, if it exists.
        versioning_elements = unparsed_elements.get("versioning", unparsed_elements)

        return DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=versioning_elements,
            valid_keys=["ogd_revision"],
            to_type=str,
            default_value=DatasetSchema._DEFAULT_OGD_REVISION,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _getEventSpecVersion(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> SemanticVersion:
        ret_val : SemanticVersion

        # 1. Get a raw 'version' value to work with.
        raw_version : Any

        # look for event spec version in the versioning section, if it exists.
        versioning_elements = unparsed_elements.get("versioning", unparsed_elements)

        raw_version = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=versioning_elements,
            valid_keys=["event_specification_version", "event_spec_version"],
            to_type=[SemanticVersion, str],
            default_value=DatasetSchema._DEFAULT_EVENT_VERSION,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True # This should stop being optional once datasets are re-run with ogd-core 1.0
        )
        match raw_version:
            case SemanticVersion():
                ret_val = raw_version
            case str():
                ret_val = SemanticVersion.FromString(raw_version, verbose=False)
            case _:
                Logger.Log(f"In DatasetSchema, raw event spec version was unexpected type {type(raw_version)}, using SemanticVersion.FromString(str(raw_version))")
                ret_val = SemanticVersion.FromString(str(raw_version))

        return ret_val
        #endregion
        
        #region Parse output info

    @staticmethod
    def _getBaseFileLocation(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationConfig]:
        ret_val : Optional[LocationConfig]

        path : LocationConfig | Path = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["base_file_location"],
            to_type=[LocationConfig, Path],
            default_value=DatasetSchema._DEFAULT_FILES_LOCATION,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match path:
            case LocationConfig() | None:
                ret_val = path
            case Path():
                ret_val = FileLocationConfig.FromPath(name=f"{schema_name}Events", fullpath=path)
            case _:
                ret_val = None
                Logger.Log(f"In DatasetSchema, raw file path for all-events file had unexpected type {type(path)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _getAllEventsFile(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationConfig]:
        ret_val : Optional[LocationConfig]

        # look for file in the outputs section, if it exists.
        outputs_elements = unparsed_elements.get("output", unparsed_elements)

        path : LocationConfig | Path = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=outputs_elements,
            valid_keys=["all_events_file", "events_file"],
            to_type=[LocationConfig, Path],
            default_value=DatasetSchema._DEFAULT_EVENTS_FILE,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match path:
            case LocationConfig() | None:
                ret_val = path
            case Path():
                ret_val = FileLocationConfig.FromPath(name=f"{schema_name}Events", fullpath=path)
            case _:
                ret_val = None
                Logger.Log(f"In DatasetSchema, raw file path for all-events file had unexpected type {type(path)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _getGameEventsFile(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationConfig]:
        ret_val : Optional[LocationConfig]

        # look for file in the outputs section, if it exists.
        outputs_elements = unparsed_elements.get("output", unparsed_elements)

        path : LocationConfig | Path  = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=outputs_elements,
            valid_keys=["game_events_file", "events_file", "raw_file"],
            to_type=[LocationConfig, Path],
            default_value=DatasetSchema._DEFAULT_RAW_FILE,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match path:
            case LocationConfig() | None:
                ret_val = path
            case Path():
                ret_val = FileLocationConfig.FromPath(name=f"{schema_name}GameEvents", fullpath=path)
            case _:
                ret_val = None
                Logger.Log(f"In DatasetSchema, raw file path for game-events file had unexpected type {type(path)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _getAllFeaturesFile(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationConfig]:
        ret_val : Optional[FileLocationConfig]

        # look for file in the outputs section, if it exists.
        outputs_elements = unparsed_elements.get("output", unparsed_elements)

        path : Path | str = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=outputs_elements,
            valid_keys=["all_features_file", "features_file", "combined_features_file"],
            to_type=[LocationConfig, Path],
            default_value=DatasetSchema._DEFAULT_COMB_FEATS_FILE,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match path:
            case LocationConfig() | None:
                ret_val = path
            case Path():
                ret_val = FileLocationConfig.FromPath(name=f"{schema_name}Features", fullpath=path)
            case _:
                ret_val = None
                Logger.Log(f"In DatasetSchema, raw file path for all-features file had unexpected type {type(path)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _getSessionsFile(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationConfig]:
        ret_val : Optional[LocationConfig]

        # look for file in the outputs section, if it exists.
        outputs_elements = unparsed_elements.get("output", unparsed_elements)

        path : LocationConfig | Path = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=outputs_elements,
            valid_keys=["sessions_file"],
            to_type=[LocationConfig, Path],
            default_value=DatasetSchema._DEFAULT_SESSIONS_FILE,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match path:
            case LocationConfig() | None:
                ret_val = path
            case Path():
                ret_val = FileLocationConfig.FromPath(name=f"{schema_name}Sessions", fullpath=path)
            case _:
                ret_val = None
                Logger.Log(f"In DatasetSchema, raw file path for session features file had unexpected type {type(path)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _getPlayersFile(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationConfig]:
        ret_val : Optional[LocationConfig]

        # look for file in the outputs section, if it exists.
        outputs_elements = unparsed_elements.get("output", unparsed_elements)

        path : LocationConfig | Path = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=outputs_elements,
            valid_keys=["players_file"],
            to_type=[LocationConfig, Path],
            default_value=DatasetSchema._DEFAULT_PLAYERS_FILE,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match path:
            case LocationConfig() | None:
                ret_val = path
            case Path():
                ret_val = FileLocationConfig.FromPath(name=f"{schema_name}Players", fullpath=path)
            case _:
                ret_val = None
                Logger.Log(f"In DatasetSchema, raw file path for player features file had unexpected type {type(path)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _getPopulationFile(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationConfig]:
        ret_val : Optional[LocationConfig]

        # look for file in the outputs section, if it exists.
        outputs_elements = unparsed_elements.get("output", unparsed_elements)

        path : LocationConfig | Path = DatasetSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=outputs_elements,
            valid_keys=["population_file"],
            to_type=[LocationConfig, Path],
            default_value=DatasetSchema._DEFAULT_POPULATION_FILE,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        match path:
            case LocationConfig() | None:
                ret_val = path
            case Path():
                ret_val = FileLocationConfig.FromPath(name=f"{schema_name}Population", fullpath=path)
            case _:
                ret_val = None
                Logger.Log(f"In DatasetSchema, raw file path for population features file had unexpected type {type(path)}, expected a path! Using {ret_val} instead")

        return ret_val
        #endregion

        #region Parse deprecated/compatibility info
        #endregion

    @staticmethod
    def _getDateModified(raw_val:Optional[date | str], unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[date]:
        """Function to obtain the modified date from a dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: date | str
        """
        ret_val : Optional[date] = None

        if raw_val is None:
            ret_val = DatasetSchema.ParseElement(
                unparsed_elements=unparsed_elements,
                valid_keys=["date_modified"],
                to_type=date,
                default_value=DatasetSchema._DEFAULT_DATE_MODIFIED,
                remove_target=True,
                schema_name=schema_name,
                optional_element=True
            )
        else:
            try:
                ret_val = conversions.ConvertToType(value=raw_val, to_type=date, name=schema_name or "DatasetSchema")
            except ValueError as err:
                Logger.Log(f"Invalid date_modified for dataset schema, expected a date, but got {raw_val}, resulting in error: {err}\nUsing {ret_val} instead")
        return ret_val

    @staticmethod
    def _getStartDate(raw_val:Optional[date | str], unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[date]:
        """Function to obtain the start date from a dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: date | str
        """
        ret_val : Optional[date] = None

        if raw_val is None:
            ret_val = DatasetSchema.ParseElement(
                unparsed_elements=unparsed_elements,
                valid_keys=["start_date"],
                to_type=date,
                default_value=DatasetSchema._DEFAULT_START_DATE,
                remove_target=True,
                schema_name=schema_name,
                optional_element=True
            )
        else:
            try:
                ret_val = conversions.ConvertToType(value=raw_val, to_type=date, name=schema_name or "DatasetSchema")
            except ValueError as err:
                Logger.Log(f"Invalid start_date for dataset schema, expected a date, but got {raw_val}, resulting in error: {err}\nUsing {ret_val} instead")
        return ret_val

    @staticmethod
    def _getEndDate(raw_val:Optional[date | str], unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[date]:
        """Function to obtain the end date from a dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: date | str
        """
        ret_val : Optional[date] = None

        if raw_val is None:
            ret_val = DatasetSchema.ParseElement(
                unparsed_elements=unparsed_elements,
                valid_keys=["end_date"],
                to_type=date,
                default_value=DatasetSchema._DEFAULT_END_DATE,
                remove_target=True,
                schema_name=schema_name,
                optional_element=True
            )
        else:
            try:
                ret_val = conversions.ConvertToType(value=raw_val, to_type=date, name=schema_name or "DatasetSchema")
            except ValueError as err:
                Logger.Log(f"Invalid end_date for dataset schema, expected a date, but got {raw_val}, resulting in error: {err}\nUsing {ret_val} instead")
        return ret_val
    #endregion

    # *** PRIVATE METHODS ***
