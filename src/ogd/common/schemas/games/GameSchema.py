# import standard libraries
import logging
from importlib.resources import files
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List, Optional, Set, Tuple, Union
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.configs.games.AggregateConfig import AggregateConfig
from ogd.common.configs.games.DetectorConfig import DetectorConfig
from ogd.common.configs.games.DetectorMapConfig import DetectorMapConfig
from ogd.common.schemas.games.DataElementSchema import DataElementSchema
from ogd.common.schemas.games.EventSchema import EventSchema
from ogd.common.configs.games.PerCountConfig import PerCountConfig
from ogd.common.configs.games.FeatureConfig import FeatureConfig
from ogd.common.configs.games.FeatureMapConfig import FeatureMapConfig
from ogd.common.models.enums.IterationMode import IterationMode
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils import fileio
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class GameSchema
class GameSchema(Schema):
    """A fairly simple class that reads a JSON schema with information on how a given
    game's data is structured in the database, and the features we want to extract
    for that game.
    The class includes several functions for easy access to the various parts of
    this schema data.
    """
    _DEFAULT_ENUMS = {}
    _DEFAULT_GAME_STATE = {}
    _DEFAULT_USER_DATA = {}
    _DEFAULT_EVENT_LIST = []
    _DEFAULT_DETECTOR_MAP = {'perlevel':{}, 'per_count':{}, 'aggregate':{}}
    _DEFAULT_AGGREGATES = {}
    _DEFAULT_PERCOUNTS = {}
    _DEFAULT_LEGACY_PERCOUNTS = {}
    _DEFAULT_LEGACY_MODE = False
    _DEFAULT_CONFIG = {}
    _DEFAULT_MIN_LEVEL = None
    _DEFAULT_MAX_LEVEL = None
    _DEFAULT_OTHER_RANGES = {}
    _DEFAULT_VERSIONS = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:str, enum_defs:Dict[str, List[str]],
                 game_state:Map, user_data:Map, event_list:List[EventSchema],
                 detector_map:Dict[str, Dict[str, DetectorConfig]],
                 aggregate_feats: Dict[str, AggregateConfig], percount_feats:Dict[str, PerCountConfig],
                 legacy_perlevel_feats: Dict[str, PerCountConfig], use_legacy_mode:bool,
                 config:Map, min_level:Optional[int], max_level:Optional[int], other_ranges:Dict[str, range],
                 supported_vers:Optional[List[int]], other_elements:Optional[Map]=None):
        """Constructor for the GameSchema class.
        Given a path and filename, it loads the data from a JSON schema,
        storing the full schema into a private variable, and compiling a list of
        all features to be extracted.

        TODO: need to get game_state from schema file, and use a GameStateSchema instead of general Map.
        TODO: Use DetectorMapSchema and FeatureMapSchema instead of just dicts... I think. Depending how these all work together.
        TODO : make parser functions for config and versions, so we can do ElementFromDict for them as well.

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: str
        :param enum_defs: _description_
        :type enum_defs: Dict[str, List[str]]
        :param game_state: _description_
        :type game_state: Map
        :param user_data: _description_
        :type user_data: Map
        :param event_list: _description_
        :type event_list: List[EventSchema]
        :param detector_map: _description_
        :type detector_map: Dict[str, Dict[str, DetectorConfig]]
        :param aggregate_feats: _description_
        :type aggregate_feats: Dict[str, AggregateConfig]
        :param percount_feats: _description_
        :type percount_feats: Dict[str, PerCountFeatures]
        :param legacy_perlevel_feats: _description_
        :type legacy_perlevel_feats: Dict[str, PerCountConfig]
        :param use_legacy_mode: _description_
        :type use_legacy_mode: bool
        :param config: _description_
        :type config: Map
        :param min_level: _description_
        :type min_level: Optional[int]
        :param max_level: _description_
        :type max_level: Optional[int]
        :param other_ranges: _description_
        :type other_ranges: Dict[str, range]
        :param supported_vers: _description_
        :type supported_vers: Optional[List[int]]
        :param other_elements: _description_
        :type other_elements: Dict[str, Any]
        :return: The new instance of GameSchema
        :rtype: GameSchema
        """
    # 1. define instance vars
        self._game_id                : str                                  = game_id
        self._enum_defs              : Dict[str, List[str]]                 = enum_defs
        self._game_state             : Map                                  = game_state
        self._user_data              : Map                                  = user_data
        self._event_list             : List[EventSchema]                    = event_list
        self._detector_map           : Dict[str, Dict[str, DetectorConfig]] = detector_map
        self._aggregate_feats        : Dict[str, AggregateConfig]           = aggregate_feats
        self._percount_feats         : Dict[str, PerCountConfig]            = percount_feats
        self._legacy_perlevel_feats  : Dict[str, PerCountConfig]            = legacy_perlevel_feats
        self._legacy_mode            : bool                                 = use_legacy_mode
        self._config                 : Map                                  = config
        self._min_level              : Optional[int]                        = min_level
        self._max_level              : Optional[int]                        = max_level
        self._other_ranges           : Dict[str, range]                     = other_ranges
        self._supported_vers         : Optional[List[int]]                  = supported_vers

        super().__init__(name=self._game_id, other_elements=other_elements)

    # def __getitem__(self, key) -> Any:
    #     return _schema[key] if _schema is not None else None

    @property
    def GameName(self) -> str:
        """Property for the name of the game configured by this schema
        """
        return self._game_id

    @property
    def EnumDefs(self) -> Dict[str, List[str]]:
        """Property for the dict of all enums defined for sub-elements in the given game's schema.
        """
        return self._enum_defs

    @property
    def GameState(self) -> Dict[str, Any]:
        """Property for the dictionary describing the structure of the GameState column for the given game.
        """
        return self._game_state

    @property
    def UserData(self) -> Dict[str, Any]:
        """Property for the dictionary describing the structure of the UserData column for the given game.
        """
        return self._user_data

    @property
    def Events(self) -> List[EventSchema]:
        """Property for the list of events the game logs.
        """
        return self._event_list

    @property
    def EventTypes(self) -> List[str]:
        """Property for the names of all event types for the game.
        """
        return [event.Name for event in self.Events]

    @property
    def Detectors(self) -> Dict[str, Dict[str, DetectorConfig]]:
        """Property for the dictionary of categorized detectors to extract.
        """
        return self._detector_map

    @property
    def DetectorNames(self) -> List[str]:
        """Property for the compiled list of all detector names.
        """
        ret_val : List[str] = []
        for _category in self.Detectors.values():
            ret_val += [detector.Name for detector in _category.values()]
        return ret_val

    @property
    def PerCountDetectors(self) -> Dict[str, DetectorConfig]:
        """Property for the dictionary of per-custom-count detectors.
        """
        return self.Detectors.get("per_count", {})

    @property
    def AggregateDetectors(self) -> Dict[str, DetectorConfig]:
        """Property for the dictionary of aggregate detectors.
        """
        return self.Detectors.get("aggregate", {})

    @property
    def Features(self) -> Dict[str, Union[Dict[str, AggregateConfig], Dict[str, PerCountConfig]]]:
        """Property for the dictionary of categorized features to extract.
        """
        return { 'aggregate' : self._aggregate_feats, 'per_count' : self._percount_feats, 'perlevel' : self._legacy_perlevel_feats }

    @property
    def FeatureNames(self) -> List[str]:
        """Property for the compiled list of all feature names.
        """
        ret_val : List[str] = []
        for _category in self.Features.values():
            ret_val += [feature.Name for feature in _category.values()]
        return ret_val

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str,PerCountConfig]:
        """Property for the dictionary of legacy per-level features
        """
        return self._legacy_perlevel_feats

    @property
    def PerCountFeatures(self) -> Dict[str,PerCountConfig]:
        """Property for the dictionary of per-custom-count features.
        """
        return self._percount_feats

    @property
    def AggregateFeatures(self) -> Dict[str,AggregateConfig]:
        """Property for the dictionary of aggregate features.
        """
        return self._aggregate_feats

    @property
    def LevelRange(self) -> range:
        """Property for the range of levels defined in the schema if any.
        """
        ret_val = range(0)
        if self._min_level is not None and self._max_level is not None:
            # for i in range(self._min_level, self._max_level+1):
            ret_val = range(self._min_level, self._max_level+1)
        else:
            Logger.Log(f"Could not generate per-level features, min_level={self._min_level} and max_level={self._max_level}", logging.ERROR)
        return ret_val

    @property
    def OtherRanges(self) -> Dict[str, range]:
        return self._other_ranges

    @property
    def Config(self) -> Dict[str, Any]:
        return self._config

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        event_summary = ["## Logged Events",
                         "The individual fields encoded in the *game_state* and *user_data* Event element for all event types, and the fields in the *event_data* Event element for each individual event type logged by the game."
                        ]
        enum_list     = ["### Enums",
                         "\n".join(
                             ["| **Name** | **Values** |",
                             "| ---      | ---        |"]
                         + [f"| {name} | {val_list} |" for name,val_list in self.EnumDefs.items()]
                        )]
        game_state_list = ["### Game State",
                           "\n".join(
                               ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                               "| ---      | ---      | ---             | ---         |"]
                           + [elem.AsMarkdownRow for elem in self.GameState.values()]
                          )]
        user_data_list = ["### User Data",
                          "\n".join(
                              ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                              "| ---      | ---      | ---             | ---         |"]
                          + [elem.AsMarkdownRow for elem in self.UserData.values()]
                         )]
        # Set up list of events
        event_list = [event.AsMarkdownTable for event in self.Events] if len(self.Events) > 0 else ["None"]
        # Set up list of detectors
        detector_summary = ["## Detected Events",
                            "The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run."
                           ]
        detector_list = []
        for detect_kind in ["perlevel", "per_count", "aggregate"]:
            if detect_kind in self._detector_map:
                detector_list += [detector.AsMarkdown for detector in self.Detectors[detect_kind].values()]
        detector_list = detector_list if len(detector_list) > 0 else ["None"]
        # Set up list of features
        feature_summary = ["## Processed Features",
                           "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        feature_list = [feature.AsMarkdown for feature in self._aggregate_feats.values()] + [feature.AsMarkdown for feature in self._percount_feats.values()]
        feature_list = feature_list if len(feature_list) > 0 else ["None"]
        # Include other elements
        other_summary = ["## Other Elements",
                         "Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors."
                         ]
        other_element_list = [ f"{key} : {self._other_elements[key]}" for key in self._other_elements.keys()]
        other_range_summary = ["### Other Ranges",
                         "Extra ranges specified in the game's schema, which may be referenced by event/feature processors."
                         ]
        other_range_list = [ f"{key} : {self.OtherRanges[key]}" for key in self.OtherRanges ]

        ret_val = "  \n\n".join(event_summary
                              + enum_list + game_state_list + user_data_list + event_list
                              + detector_summary + detector_list
                              + feature_summary + feature_list
                              + other_summary + other_element_list
                              + other_range_summary + other_range_list)

        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "GameSchema":
    # 1. define local vars
        _game_id                : str                                  = name
        _enum_defs              : Dict[str, List[str]]
        _game_state             : Dict[str, Any]
        _user_data              : Dict[str, Any]
        _event_list             : List[EventSchema]
        _detector_map           : Dict[str, Dict[str, DetectorConfig]]
        _aggregate_feats        : Dict[str, AggregateConfig] = {}
        _percount_feats         : Dict[str, PerCountConfig]  = {}
        _legacy_perlevel_feats  : Dict[str, PerCountConfig]  = {}
        _legacy_mode            : bool
        _config                 : Dict[str, Any]
        _min_level              : Optional[int]
        _max_level              : Optional[int]
        _other_ranges           : Dict[str, range]
        _supported_vers         : Optional[List[int]]

        if not isinstance(all_elements, dict):
            all_elements   = {}
            Logger.Log(f"For {_game_id} GameSchema, all_elements was not a dict, defaulting to empty dict", logging.WARN)

    # 2. set instance vars, starting with event data

        _enum_defs = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["enums"],
            parser_function=cls._parseEnumDefs,
            default_value=cls._DEFAULT_ENUMS
        )
        _game_state = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["game_state"],
            parser_function=cls._parseGameState,
            default_value=cls._DEFAULT_GAME_STATE
        )
        _user_data = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["user_data"],
            parser_function=cls._parseUserData,
            default_value=cls._DEFAULT_USER_DATA
        )
        _event_list = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["events"],
            parser_function=cls._parseEventList,
            default_value=cls._DEFAULT_EVENT_LIST
        )

    # 3. Get detector information
        _detector_map = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["detectors"],
            parser_function=cls._parseDetectorMap,
            default_value=cls._DEFAULT_DETECTOR_MAP
        )
        _detector_map = _detector_map.AsDict # TODO : investigate weird Dict[str, Dict[str, DetectorConfig]] type inference

    # 4. Get feature information
        _feat_map = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["features"],
            parser_function=cls._parseFeatureMap,
            default_value={}
        )
        _aggregate_feats.update(_feat_map.AggregateFeatures)
        _percount_feats.update(_feat_map.PerCountFeatures)
        _legacy_perlevel_feats.update(_feat_map.LegacyPerLevelFeatures)
        _legacy_mode = _feat_map.LegacyMode

    # 5. Get config, if any
        if "config" in all_elements.keys():
            _config = all_elements['config']
        else:
            Logger.Log(f"{_game_id} game schema does not define any config items.", logging.INFO)
        if "SUPPORTED_VERS" in _config:
            _supported_vers = _config['SUPPORTED_VERS']
        else:
            _supported_vers = None
            Logger.Log(f"{_game_id} game schema does not define supported versions, defaulting to support all versions.", logging.INFO)

    # 6. Get level range and other ranges, if any
        if "level_range" in all_elements.keys():
            _min_level, _max_level = cls._parseLevelRange(all_elements['level_range'])
        else:
            Logger.Log(f"{_game_id} game schema does not define a level range.", logging.INFO)

        _other_ranges = {key : range(val.get('min', 0), val.get('max', 1)) for key,val in all_elements.items() if key.endswith("_range")}

    # 7. Collect any other, unexpected elements
        _used = {'enums', 'game_state', 'user_data', 'events', 'detectors', 'features', 'level_range', 'config'}.union(_other_ranges.keys())
        _leftovers = { key:val for key,val in all_elements.items() if key not in _used }
        return GameSchema(name=name, game_id=_game_id, enum_defs=_enum_defs,
                          game_state=_game_state, user_data=_user_data,
                          event_list=_event_list, detector_map=_detector_map,
                          aggregate_feats=_aggregate_feats, percount_feats=_percount_feats,
                          legacy_perlevel_feats=_legacy_perlevel_feats, use_legacy_mode=_legacy_mode,
                          config=_config, min_level=_min_level, max_level=_max_level,
                          other_ranges=_other_ranges, supported_vers=_supported_vers,
                          other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "GameSchema":
        return GameSchema(
            name="DefaultGameSchema",
            game_id="DEFAULT_GAME",
            enum_defs=cls._DEFAULT_ENUMS,
            game_state=cls._DEFAULT_GAME_STATE,
            user_data=cls._DEFAULT_USER_DATA,
            event_list=cls._DEFAULT_EVENT_LIST,
            detector_map=cls._DEFAULT_DETECTOR_MAP,
            aggregate_feats=cls._DEFAULT_AGGREGATES,
            percount_feats=cls._DEFAULT_PERCOUNTS,
            legacy_perlevel_feats=cls._DEFAULT_LEGACY_PERCOUNTS,
            use_legacy_mode=cls._DEFAULT_LEGACY_MODE,
            config=cls._DEFAULT_CONFIG,
            min_level=cls._DEFAULT_MIN_LEVEL,
            max_level=cls._DEFAULT_MAX_LEVEL,
            other_ranges=cls._DEFAULT_OTHER_RANGES,
            supported_vers=cls._DEFAULT_VERSIONS,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    @staticmethod
    def FromFile(game_id:str, schema_path:Optional[Path] = None):
        # Give schema_path a default, don't think we can use game_id to construct it directly in the function header (so do it here if None)
        schema_path = schema_path or Path("./") / "ogd" / "games" / game_id / "schemas"
        all_elements = GameSchema._loadSchemaFile(game_name=game_id, schema_path=schema_path)
        return GameSchema.FromDict(name=game_id, all_elements=all_elements or {})

    # *** PUBLIC METHODS ***

    def GetCountRange(self, count:Any) -> range:
        """Function to get a predefined range for per-count features, or to generate a range up to given count.
        Typically, this would be used to retrieve the `level_range` for the game.
        However, any other ranges defined in the game's schema can be retrieved here, or a custom range object generated (using `int(count)`).

        :param count: The name of a range defined in the game schema, or an object that can be int-ified to define a custom range.
        :type count: Any
        :return: The range object with name given by `count`, or a new range from 0 to (but not including) `int(count)`
        :rtype: range
        """
        if isinstance(count, str):
            if count.lower() == "level_range":
                count_range = self.LevelRange
            elif count in self.OtherRanges.keys():
                count_range = self.OtherRanges.get(count, range(0))
            else:
                other_range : Dict[str, int] = self.NonStandardElements.get(count, {'min':0, 'max':-1})
                count_range = range(other_range['min'], other_range['max']+1)
        else:
            count_range = range(0,int(count))
        return count_range

    def DetectorEnabled(self, detector_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode) -> bool:
        """Function to check if detector with given base name and iteration mode (aggregate or percount) is enabled for given extract mode.

        :param detector_name: The base name of the detector class to check
        :type detector_name: str
        :param iter_mode: The "iteration" mode of the detector class (aggregate or per-count)
        :type iter_mode: IterationMode
        :param extract_mode: The extraction mode of the detector (which... should always be detector?)
        :type extract_mode: ExtractionMode
        :raises ValueError: Error indicating an unrecognized iteration mode was given.
        :return: True if the given detector is enabled in the schema, otherwise False
        :rtype: bool
        """
        if self._legacy_mode:
            return False
        ret_val : bool

        _detector_schema : Optional[DetectorConfig]
        match iter_mode:
            case IterationMode.AGGREGATE:
                _detector_schema = self.Detectors['aggregate'].get(detector_name)
            case IterationMode.PERCOUNT:
                _detector_schema = self.Detectors['per_count'].get(detector_name, self.Detectors['perlevel'].get(detector_name))
            case _:
                raise ValueError(f"In GameSchema, DetectorEnabled was given an unrecognized iteration mode of {iter_mode.name}")
        if _detector_schema is not None:
            ret_val = extract_mode in _detector_schema.Enabled
        else:
            Logger.Log(f"Could not find detector {detector_name} in schema for {iter_mode.name} mode")
            ret_val = False
        return ret_val

    def FeatureEnabled(self, feature_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode) -> bool:
        if self._legacy_mode:
            return feature_name == "legacy"
        ret_val : bool

        _feature_schema : Optional[FeatureConfig]
        match iter_mode:
            case IterationMode.AGGREGATE:
                _feature_schema = self.AggregateFeatures.get(feature_name)
            case IterationMode.PERCOUNT:
                _feature_schema = self.PerCountFeatures.get(feature_name)
            case _:
                raise ValueError(f"In GameSchema, FeatureEnabled was given an unrecognized iteration mode of {iter_mode.name}")
        if _feature_schema is not None:
            ret_val = extract_mode in _feature_schema.Enabled
        else:
            Logger.Log(f"Could not find feature {feature_name} in schema for {iter_mode.name} mode")
            ret_val = False
        return ret_val

    def EnabledDetectors(self, iter_modes:Set[IterationMode], extract_modes:Set[ExtractionMode]=set()) -> Dict[str, DetectorConfig]:
        if self._legacy_mode:
            return {}
        ret_val : Dict[str, DetectorConfig] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateDetectors.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountDetectors.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    def EnabledFeatures(self, iter_modes:Set[IterationMode]={IterationMode.AGGREGATE, IterationMode.PERCOUNT}, extract_modes:Set[ExtractionMode]=set()) -> Dict[str, FeatureConfig]:
        if self._legacy_mode:
            return {"legacy" : AggregateConfig("legacy", {"type":"legacy", "return_type":None, "description":"", "enabled":True})} if IterationMode.AGGREGATE in iter_modes else {}
        ret_val : Dict[str, FeatureConfig] = {}

        if IterationMode.AGGREGATE in iter_modes:
            ret_val.update({key:val for key,val in self.AggregateFeatures.items() if val.Enabled.issuperset(extract_modes)})
        if IterationMode.PERCOUNT in iter_modes:
            ret_val.update({key:val for key,val in self.PerCountFeatures.items() if val.Enabled.issuperset(extract_modes)})
        return ret_val

    # *** PRIVATE STATICS ***

    @staticmethod
    def _loadSchemaFile(game_name:str, schema_path:Path) -> Optional[Dict[Any, Any]]:
        ret_val = None

        # 1. make sure the name and path are in the right form.
        schema_name = f"{game_name.upper()}.json"
        # 2. try to actually load the contents of the file.
        try:
            ret_val = fileio.loadJSONFile(filename=schema_name, path=schema_path)
        except (ModuleNotFoundError, FileNotFoundError):
            Logger.Log(f"Unable to load GameSchema for {game_name}, {schema_name} does not exist! Trying to load from json template instead...", logging.WARN, depth=1)
            ret_val = GameSchema._schemaFromTemplate(schema_path=schema_path, schema_name=schema_name)
            if ret_val is not None:
                Logger.Log(f"Loaded schema for {game_name} from template.", logging.WARN, depth=1)
            else:
                Logger.Log(f"Failed to load schema for {game_name} from template.", logging.WARN, depth=1)
        else:
            if ret_val is None:
                Logger.Log(f"Could not load game schema at {schema_path / schema_name}, the file was empty!", logging.ERROR)
        return ret_val

    @staticmethod
    def _schemaFromTemplate(schema_path:Path, schema_name:str) -> Optional[Dict[Any, Any]]:
        ret_val = None

        template_name = schema_name + ".template"
        try:
            ret_val = fileio.loadJSONFile(filename=template_name, path=schema_path, autocorrect_extension=False)
        except FileNotFoundError:
            Logger.Log(       f"Could not load {schema_name} from template, the template does not exist at {schema_path}.", logging.WARN, depth=2)
            print(f"(via print) Could not create {schema_name} from template, the template does not exist at {schema_path}.")
        else:
            Logger.Log(f"Trying to copy {schema_name} from template, for future use...", logging.DEBUG, depth=2)
            template = schema_path / template_name
            try:
                copyfile(template, schema_path / schema_name)
            except Exception as cp_err:
                Logger.Log(       f"Could not copy {schema_name} from template, a {type(cp_err)} error occurred:\n{cp_err}", logging.WARN, depth=2)
                print(f"(via print) Could not copy {schema_name} from template, a {type(cp_err)} error occurred:\n{cp_err}")
            else:
                Logger.Log(       f"Successfully copied {schema_name} from template.", logging.DEBUG, depth=2)
        return ret_val


    @staticmethod
    def _parseEnumDefs(enums_list:Dict[str, Any]) -> Dict[str, List[str]]:
        ret_val : Dict[str, List[str]]
        if isinstance(enums_list, dict):
            ret_val = enums_list
        else:
            ret_val = {}
            Logger.Log(f"enums_list was unexpected type {type(enums_list)}, defaulting to empty Dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameState(game_state:Dict[str, Any]) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]
        if isinstance(game_state, dict):
            ret_val = {name:DataElementSchema.FromDict(name=name, all_elements=elems) for name,elems in game_state.items()}
        else:
            ret_val = {}
            Logger.Log(f"game_state was unexpected type {type(game_state)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseUserData(user_data:Dict[str, Any]) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]
        if isinstance(user_data, dict):
            ret_val = {name:DataElementSchema.FromDict(name=name, all_elements=elems) for name,elems in user_data.items()}
        else:
            ret_val = {}
            Logger.Log(f"user_data was unexpected type {type(user_data)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseEventList(events_list:Dict[str, Any]) -> List[EventSchema]:
        ret_val : List[EventSchema]
        if isinstance(events_list, dict):
            ret_val = [EventSchema.FromDict(name=key, all_elements=val) for key,val in events_list.items()]
        else:
            ret_val = []
            Logger.Log(f"events_list was unexpected type {type(events_list)}, defaulting to empty List.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDetectorMap(detector_map:Dict[str, Any]) -> DetectorMapSchema:
        ret_val : DetectorMapSchema
        if isinstance(detector_map, dict):
            ret_val = DetectorMapSchema.FromDict(name=f"Detectors", all_elements=detector_map)
        else:
            ret_val = DetectorMapSchema.FromDict(name="Empty Features", all_elements={})
            Logger.Log(f"detector_map was unexpected type {type(detector_map)}, defaulting to empty map.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseFeatureMap(feature_map:Dict[str, Any]) -> FeatureMapSchema:
        ret_val : FeatureMapSchema
        if isinstance(feature_map, dict):
            ret_val = FeatureMapSchema.FromDict(name=f"Features", all_elements=feature_map)
        else:
            ret_val = FeatureMapSchema.FromDict(name="Empty Features", all_elements={})
            Logger.Log(f"feature_map was unexpected type {type(feature_map)}, defaulting to empty map.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseLevelRange(level_range:Dict[str, int]) -> Tuple[Optional[int], Optional[int]]:
        ret_val : Tuple[Optional[int], Optional[int]]
        if isinstance(level_range, dict):
            ret_val = (level_range.get("min", None), level_range.get("max", None))
        else:
            ret_val = (None, None)
            Logger.Log(f"level_range was unexpected type {type(level_range)}, defaulting to no specified range.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
