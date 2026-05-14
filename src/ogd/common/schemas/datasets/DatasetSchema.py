# standard imports
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Self

# ogd imports
from ogd.common.filters.Filter import Filter
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.schemas.events.EventSchema import EventSchema
from ogd.common.schemas.events.GameStateSchema import GameStateSchema
from ogd.common.schemas.features.FeatureSchema import FeatureSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map
from ogd.common.models.SemanticVersion import SemanticVersion

class DatasetSchema(Schema):
    """DatasetSchema struct

    TODO : Fill in description
    TODO : Add a _parseKey function, rather than having logic for that part sit naked in FromDict
    TODO : Deal with how to handle game ID, particularly since we don't typically include the game ID in dictionaries when using FromDict
    """
    _DEFAULT_GAME_ID             : Final[str]                     = "DEFAULT GAME"
    _DEFAULT_DATASET_ID          : Final[DatasetKey]              = DatasetKey.Default()
    # Population info
    _DEFAULT_FILTERS             : Final[Dict[str, str | Filter]] = {}
    _DEFAULT_SESSION_COUNT       : Final[int]                     = 0
    _DEFAULT_PLAYER_COUNT        : Final[int]                     = 0
    # Event info
    _DEFAULT_GAME_STATE          : Final[GameStateSchema]         = GameStateSchema.Default()
    _DEFAULT_EVENTS              : Final[Dict[str, EventSchema]]  = {}
    # feature info
    _DEFAULT_FEATURES            : Final[Dict[str, FeatureSchema]] = {}
    # version info
    _DEFAULT_OGD_VERSION         : Final[str]                     = "UNKNOWN OGD VERSION"
    _DEFAULT_OGD_REVISION        : Final[str]                     = "UNKNOWN OGD REVISION"
    _DEFAULT_EVENT_VERSION       : Final[str]                     = "UNKNOWN EVENT SCHEMA VERSION"
    # output info
    _DEFAULT_FILES_LOCATION      : Final[Path]                    = Path("data/")
    _DEFAULT_RAW_FILE            : Final[None]                    = None
    _DEFAULT_EVENTS_FILE         : Final[None]                    = None
    _DEFAULT_COMB_FEATS_FILE     : Final[None]                    = None
    _DEFAULT_SESSIONS_FILE       : Final[None]                    = None
    _DEFAULT_PLAYERS_FILE        : Final[None]                    = None
    _DEFAULT_POPULATION_FILE     : Final[None]                    = None
    # deprecated, compatibility info
    _DEFAULT_DATE_MODIFIED       : Final[str]                     = "UNKNOWN DATE"
    _DEFAULT_START_DATE          : Final[str]                     = "UNKNOWN DATE"
    _DEFAULT_END_DATE            : Final[str]                     = "UNKNOWN DATE"

    # *** BUILT-INS & PROPERTIES ***

    # TODO : overload versions for individual parts of logging spec schema, vs. passing in a whole log spec schema
    def __init__(self, name:str, game_id:Optional[str],       dataset_id:Optional[DatasetKey],
                 filters:Optional[Dict[str, str | Filter]],   session_ct:Optional[int],                 player_ct:Optional[int],
                 game_state:Optional[GameStateSchema],        events:Optional[Dict[str, EventSchema]],  features:Optional[Dict[str, FeatureSchema]],
                 ogd_version:Optional[SemanticVersion | str], ogd_revision:Optional[str],               event_spec_version:Optional[SemanticVersion | str],
                 base_files_location:Optional[Path],
                 game_events_file:Optional[LocationSchema],   all_events_file:Optional[LocationSchema], combined_feats_file:Optional[LocationSchema],
                 sessions_file:Optional[LocationSchema],      players_file:Optional[LocationSchema],    population_file:Optional[LocationSchema],
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
        self._session_ct          : Optional[int]                    = session_ct          if session_ct          is not None else self._parseSessionCount(unparsed_elements=unparsed_elements, schema_name=name)
        self._player_ct           : Optional[int]                    = player_ct           if player_ct           is not None else self._parsePlayerCount(unparsed_elements=unparsed_elements, schema_name=name)
        self._filters             : Dict[str, str | Filter]          = filters             if filters             is not None else self._parseFilters(unparsed_elements=unparsed_elements, schema_name=name)
    # 2. Set event info
        self._game_state          : Optional[GameStateSchema]        = game_state          if game_state          is not None else self._parseGameState(unparsed_elements=unparsed_elements, schema_name=name)
        self._events              : Optional[Dict[str, EventSchema]] = events              if events              is not None else self._parseEvents(unparsed_elements=unparsed_elements, schema_name=name)
    # 3. Set feature info
        self._features            : Optional[Dict[str, FeatureSchema]] = features          if features            is not None else self._parseFeatures(unparsed_elements=unparsed_elements, schema_name=name)
    # 4. Set version info
        self._ogd_version         : SemanticVersion                  = self._toOGDVersion(version=ogd_version, fallbacks=unparsed_elements, schema_name=name)
        self._ogd_revision        : str                              = ogd_revision        if ogd_revision        is not None else self._parseOGDRevision(unparsed_elements=unparsed_elements, schema_name=name)
        self._evt_spec_version    : SemanticVersion                  = self._toEventSpecVersion(version=event_spec_version, fallbacks=unparsed_elements, schema_name=name)
    # 5. Set output info
        self._base_files_location : Path                             = base_files_location if base_files_location is not None else self._DEFAULT_FILES_LOCATION
        self._all_events_file     : Optional[LocationSchema]         = all_events_file     if all_events_file     is not None else self._parseAllEventsFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._game_events_file    : Optional[LocationSchema]         = game_events_file    if game_events_file    is not None else self._parseGameEventsFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._all_features_file   : Optional[LocationSchema]         = combined_feats_file if combined_feats_file is not None else self._parseAllFeaturesFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._sessions_file       : Optional[LocationSchema]         = sessions_file       if sessions_file       is not None else self._parseSessionsFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._players_file        : Optional[LocationSchema]         = players_file        if players_file        is not None else self._parsePlayersFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._population_file     : Optional[LocationSchema]         = population_file     if population_file     is not None else self._parsePopulationFile(unparsed_elements=unparsed_elements, schema_name=name)
    # 6. Set deprecated/compatibility info
        self._date_modified       : date | str                       = date_modified       if date_modified       is not None else self._parseDateModified(unparsed_elements=unparsed_elements, schema_name=name)
        self._start_date          : date | str                       = start_date          if start_date          is not None else self._parseStartDate(unparsed_elements=unparsed_elements, schema_name=name)
        self._end_date            : date | str                       = end_date            if end_date            is not None else self._parseEndDate(unparsed_elements=unparsed_elements, schema_name=name)
    # Finally, get key
        self._key                 : DatasetKey                       = dataset_id          if dataset_id          is not None else DatasetKey(game_id=game_id or name, from_date=self._start_date, to_date=self._end_date)
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

    # TODO : all the location schema stuff is screwy; for now types assume general LocationSchema, since in the future we could use paths or URLS.
    # Meanwhile, all the literal implementation details assume we're using paths, i.e. FileLocationSchemas.

    @property
    def GameEventsFile(self) -> Optional[Path]:
        return self._base_files_location / self._game_events_file.Location if self._game_events_file else None
    @property
    def HasGameEventsFile(self) -> bool:
        return self._game_events_file is not None
    @property
    def RawEventsFile(self) -> Optional[Path]:
        """Alias for GameEventsFile

        :return: _description_
        :rtype: Optional[Path]
        """
        return self.GameEventsFile

    @property
    def AllEventsFile(self) -> Optional[Path]:
        return self._base_files_location/ self._all_events_file.Location if self._all_events_file else None
    @property
    def HasAllEventsFile(self) -> bool:
        return self.AllEventsFile is not None
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
        return self.CombinedFeaturesFile
    @property
    def CombinedFeaturesFile(self) -> Optional[Path]:
        return self._base_files_location / self._all_features_file.Location if self._all_features_file else None
    @property
    def HasCombinedFeaturesFile(self) -> bool:
        return self.CombinedFeaturesFile is not None
    
    @property
    def SessionsFile(self) -> Optional[Path]:
        return self._base_files_location / self._sessions_file.Location if self._sessions_file else None
    @property
    def HasSessionsFile(self) -> bool:
        return self.SessionsFile is not None

    @property
    def PlayersFile(self) -> Optional[Path]:
        return self._base_files_location / self._players_file.Location if self._players_file else None
    @property
    def HasPlayersFile(self) -> bool:
        return self.PlayersFile is not None

    @property
    def PopulationFile(self) -> Optional[Path]:
        return self._base_files_location / self._population_file.Location if self._population_file else None
    @property
    def HasPopulationFile(self) -> bool:
        return self.PopulationFile is not None

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

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = \
f"""{self.Name}: {self.PlayerCount} players across {self.SessionCount} sessions.  
Last modified {self.DateModified.strftime('%m/%d/%Y') if type(self.DateModified) == date else self.DateModified} with OGD v.{self.OGDRevision or 'UNKNOWN'}  
- Files: [{self.FileSet}]"""
        return ret_val

    @property
    def AsMetadata(self) -> Dict[str, Optional[int | str | List | Dict]]:
        return self.AsDict

    @property
    def AsDict(self) -> Dict[str, Any]:
        return {
            "game_id"            : self.Key.GameID,
            "dataset_id"         : str(self.Key),
            # population info
            "session_count"      : self.SessionCount,
            "player_count"       : self.SessionCount,
            "filters"            : {name:str(filt) for name,filt in self.Filters.items()},
            # event info
            "game_state"         : self.GameState.AsDict if self.GameState else None,
            "events"             : { key : event.AsDict for key,event in self.Events.items() } if self.Events else None,
            # feature info
            "features"           : { key : feature.AsDict for key,feature in self.Features.items() } if self.Features else None,
            # version info
            "ogd_version"        : str(self.OGDVersion),
            "ogd_revision"       : self.OGDRevision,
            "event_spec_version" : str(self.EventSpecificationVersion),
            # output info
            "base_file_location" : str(self._base_files_location),
            "all_events_file"    : self._all_events_file.Location   if self._all_events_file   else None,
            "game_events_file"   : self._game_events_file.Location  if self._game_events_file  else None,
            "all_features_file"  : self._all_features_file.Location if self._all_features_file else None,
            "sessions_file"      : self._sessions_file.Location     if self._sessions_file     else None,
            "players_file"       : self._players_file.Location      if self._players_file      else None,
            "population_file"    : self._population_file.Location   if self._population_file   else None,
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

        #region Parse population info
    @staticmethod
    def _parseSessionCount(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[int]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["sessions", "session_count"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_SESSION_COUNT,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parsePlayerCount(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[int]:
        return DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["players", "player_count"],
            to_type=int,
            default_value=DatasetSchema._DEFAULT_PLAYER_COUNT,
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
        #endregion

        #region Parse event info
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
    def _parseEvents(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, EventSchema]:
        ret_val : Dict[str, EventSchema]

        raw_events = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_EVENTS,
            remove_target=True,
            schema_name=schema_name
        )
        ret_val = {
            event_name : EventSchema.FromDict(name=event_name, unparsed_elements=raw_event)
            for event_name, raw_event in raw_events
        }

        return ret_val
        #endregion

        #region Parse feature info
    @staticmethod
    def _parseFeatures(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, FeatureSchema]:
        ret_val : Dict[str, FeatureSchema]

        raw_features = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["features"],
            to_type=dict,
            default_value=DatasetSchema._DEFAULT_FEATURES,
            remove_target=True,
            schema_name=schema_name
        )
        ret_val = {
            feat_name : FeatureSchema.FromDict(name=feat_name, unparsed_elements=raw_feat)
            for feat_name, raw_feat in raw_features
        }

        return ret_val
        #endregion

        #region Parse version info
    @staticmethod
    def _toOGDVersion(version:Optional[SemanticVersion | str], fallbacks:Map, schema_name:Optional[str]=None) -> SemanticVersion:
        ret_val : SemanticVersion
        if isinstance(version, SemanticVersion):
            ret_val = version
        elif isinstance(version, str):
            ret_val = SemanticVersion.FromString(semver=version, verbose=False)
        else:
            ret_val = DatasetSchema._parseOGDVersion(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _parseOGDVersion(unparsed_elements:Map, schema_name:Optional[str]=None) -> SemanticVersion:
        ret_val : SemanticVersion

        raw_version = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["ogd_version"],
            to_type=str,
            default_value=DatasetSchema._DEFAULT_OGD_VERSION,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_version, SemanticVersion):
            ret_val = raw_version
        elif isinstance(raw_version, str):
            ret_val = SemanticVersion.FromString(raw_version)
        else:
            Logger.Log(f"In DatasetSchema, raw OGD version was unexpected type {type(raw_version)}, using SemanticVersion.FromString(str(raw_version))")
            ret_val = SemanticVersion.FromString(str(raw_version))

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
    def _toEventSpecVersion(version:Optional[SemanticVersion | str], fallbacks:Map, schema_name:Optional[str]=None) -> SemanticVersion:
        ret_val : SemanticVersion
        if isinstance(version, SemanticVersion):
            ret_val = version
        elif isinstance(version, str):
            ret_val = SemanticVersion.FromString(semver=version, verbose=False)
        else:
            ret_val = DatasetSchema._parseEventSpecVersion(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _parseEventSpecVersion(unparsed_elements:Map, schema_name:Optional[str]=None) -> SemanticVersion:
        ret_val : SemanticVersion

        raw_version = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_specification_version", "event_spec_version"],
            to_type=str,
            default_value=DatasetSchema._DEFAULT_EVENT_VERSION,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_version, SemanticVersion):
            ret_val = raw_version
        elif isinstance(raw_version, str):
            ret_val = SemanticVersion.FromString(raw_version)
        else:
            Logger.Log(f"In DatasetSchema, raw event spec version was unexpected type {type(raw_version)}, using SemanticVersion.FromString(str(raw_version))")
            ret_val = SemanticVersion.FromString(str(raw_version))

        return ret_val
        #endregion
        
        #region Parse output info
    @staticmethod
    def _parseAllEventsFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationSchema]:
        ret_val : Optional[FileLocationSchema]

        raw_loc : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["all_events_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_EVENTS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_loc, Path) or raw_loc is None:
            ret_val = FileLocationSchema.FromPath(name=f"{schema_name}Events", fullpath=raw_loc)
        else:
            ret_val = None
            Logger.Log(f"In DatasetSchema, raw file path for all-events file had unexpected type {type(raw_loc)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseGameEventsFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationSchema]:
        ret_val : Optional[FileLocationSchema]

        raw_loc : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_RAW_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_loc, Path) or raw_loc is None:
            ret_val = FileLocationSchema.FromPath(name=f"{schema_name}GameEvents", fullpath=raw_loc)
        else:
            ret_val = None
            Logger.Log(f"In DatasetSchema, raw file path for game-events file had unexpected type {type(raw_loc)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseAllFeaturesFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationSchema]:
        ret_val : Optional[FileLocationSchema]

        raw_loc : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["all_features_file", "features_file", "combined_features_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_COMB_FEATS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_loc, Path) or raw_loc is None:
            ret_val = FileLocationSchema.FromPath(name=f"{schema_name}Features", fullpath=raw_loc)
        else:
            ret_val = None
            Logger.Log(f"In DatasetSchema, raw file path for all-features file had unexpected type {type(raw_loc)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parseSessionsFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationSchema]:
        ret_val : Optional[FileLocationSchema]

        raw_loc : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["sessions_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_SESSIONS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_loc, Path) or raw_loc is None:
            ret_val = FileLocationSchema.FromPath(name=f"{schema_name}Sessions", fullpath=raw_loc)
        else:
            ret_val = None
            Logger.Log(f"In DatasetSchema, raw file path for session features file had unexpected type {type(raw_loc)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePlayersFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationSchema]:
        ret_val : Optional[FileLocationSchema]

        raw_loc : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["players_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_PLAYERS_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_loc, Path) or raw_loc is None:
            ret_val = FileLocationSchema.FromPath(name=f"{schema_name}Players", fullpath=raw_loc)
        else:
            ret_val = None
            Logger.Log(f"In DatasetSchema, raw file path for player features file had unexpected type {type(raw_loc)}, expected a path! Using {ret_val} instead")

        return ret_val

    @staticmethod
    def _parsePopulationFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[LocationSchema]:
        ret_val : Optional[FileLocationSchema]

        raw_loc : Path | str = DatasetSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["population_file"],
            to_type=Path,
            default_value=DatasetSchema._DEFAULT_POPULATION_FILE,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_loc, Path) or raw_loc is None:
            ret_val = FileLocationSchema.FromPath(name=f"{schema_name}Population", fullpath=raw_loc)
        else:
            ret_val = None
            Logger.Log(f"In DatasetSchema, raw file path for population features file had unexpected type {type(raw_loc)}, expected a path! Using {ret_val} instead")

        return ret_val
        #endregion

        #region Parse deprecated/compatibility info
        #endregion

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
    #endregion

    # *** PRIVATE METHODS ***
