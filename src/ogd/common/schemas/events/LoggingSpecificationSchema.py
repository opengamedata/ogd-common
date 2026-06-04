# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Self
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.events.DataElementSchema import DataElementSchema
from ogd.common.schemas.events.GameStateSchema import GameStateSchema
from ogd.common.schemas.events.EventSchema import EventSchema
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import JSONMap, Map

## @class LoggingSpecificationSchema
class LoggingSpecificationSchema(Schema):
    """Class for loading a game's logging specification file.

    These contain information on the structure of the `game_state` and `user_data` elements logged with every event from the game,
    as well as descriptions of each type of event the game logs.
    Further, there is information on any de facto enums that are defined for portions of the log data
    (i.e. sets of valid string values for a particular key in `game_state`, `user_data`, or `event_data`)
    And finally, it specifies which logging version of the game is so documented, as well as the folder where the particular game's schema folder resides.
    """
    _DEFAULT_ENUMS       : Final[Dict[str, List[str]]] = {}
    _DEFAULT_GAME_STATE  : Final[GameStateSchema]      = GameStateSchema.Default()
    _DEFAULT_USER_DATA   : Final[Map]                  = {}
    _DEFAULT_EVENT_LIST  : Final[List[EventSchema]]    = []
    _DEFAULT_LOG_VERSION : Final[SemanticVersion]      = SemanticVersion(0)
    _DEFAULT_GAME_FOLDER : Final[Path]                 = Path("./") / "ogd" / "games"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:str, enum_defs:Optional[Dict[str, List[str]]],
                 game_state:Optional[GameStateSchema | Map], user_data:Optional[Map],
                 event_list:Optional[List[EventSchema] | List[Map] | Map],
                 logging_version:Optional[SemanticVersion | int | str], other_elements:Optional[Map]=None):
        """Constructor for the `LoggingSpecificationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "enumas": {
                "EnumOne": [ "VALUE1", "VALUE2", "VALUE3", ... ],
                ...
            }
            "game_state": {
                "game_state_element_name": {
                    "type": "float",
                    "description": "Description of the data element of the game_state column."
                },
                ...
            },
            "user_data": {
                "user_data_element_name": {
                    "type": "float",
                    "description": "Description of the data element of the user_data column."
                },
                ...
            },
            "events": {
                "event_name" : {
                    "description": "Description of what the event is and when it occurs.",
                    "event_data": {
                        "data_element_name": {
                        "type": "bool",
                        "description": "Description of what the data element means or represents."
                        },
                        ...
                    }
                }
            },
            "logging_version" : 1
        },
        ```

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
        :param log_version: _description_
        :type log_version: int
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

    # 1. define instance vars
        self._game_id     : str                  = game_id
        self._enum_defs   : Dict[str, List[str]] = self._getEnumDefs(raw_val=enum_defs, unparsed_elements=unparsed_elements, schema_name=name)
        self._game_state  : GameStateSchema      = self._getGameState(raw_val=game_state, unparsed_elements=unparsed_elements, schema_name=name)
        self._user_data   : Map                  = self._getUserData(raw_val=user_data, unparsed_elements=unparsed_elements, schema_name=name)
        self._event_list  : List[EventSchema]    = self._getEventList(raw_val=event_list, unparsed_elements=unparsed_elements, schema_name=name)
        self._log_version : SemanticVersion      = self._getLogVersion(raw_val=logging_version, unparsed_elements=unparsed_elements, schema_name=name)

        super().__init__(name=name, other_elements=other_elements)

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
    def GameState(self) -> GameStateSchema:
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
    def EventNames(self) -> List[str]:
        """Property for the names of all event types for the game.
        """
        return [event.Name for event in self.Events]
    @property
    def EventTypes(self) -> List[str]:
        """Alias for the EventNames Property
        """
        return self.EventNames

    @property
    def LoggingVersion(self) -> SemanticVersion:
        return self._log_version

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
        game_state_list = [self.GameState.AsMarkdownTable]
        user_data_list = ["### User Data",
                          "\n".join(
                              ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                              "| ---      | ---      | ---             | ---         |"]
                          + [elem.AsMarkdownRow for elem in self.UserData.values()]
                         )]
        # Set up list of events
        event_list = [event.AsMarkdownTable for event in self.Events] if len(self.Events) > 0 else ["None"]
        # Include other elements
        other_summary = ["## Other Elements",
                         "Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors."
                         ]
        other_element_list = [ f"{key} : {self._other_elements[key]}" for key in self._other_elements.keys()]

        ret_val = "  \n\n".join(event_summary
                              + enum_list + game_state_list + user_data_list + event_list
                              + other_summary + other_element_list)

        return ret_val

    @property
    def AsDict(self) -> JSONMap:
        return {
            "enums":self.EnumDefs,
            "game_state":self.GameState.AsDict,
            "user_data":self.UserData,
            "events":{elem.Name:elem.AsDict for elem in self.Events},
            "log_version":str(self.LoggingVersion)
        }

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "LoggingSpecificationSchema":
        """_summary_

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :raises ValueError: _description_
        :raises ValueError: _description_
        :return: _description_
        :rtype: LoggingSpecificationSchema
        """
        _game_id     : str                  = name
        return LoggingSpecificationSchema(name=name, game_id=_game_id, enum_defs=None,
                          game_state=None, user_data=None,
                          event_list=None, logging_version=None,
                          other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "LoggingSpecificationSchema":
        return LoggingSpecificationSchema(
            name="DefaultLoggingSpecificationSchema",
            game_id="DEFAULT_GAME",
            enum_defs=cls._DEFAULT_ENUMS,
            game_state=cls._DEFAULT_GAME_STATE,
            user_data=cls._DEFAULT_USER_DATA,
            event_list=cls._DEFAULT_EVENT_LIST,
            logging_version=cls._DEFAULT_LOG_VERSION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _getEnumDefs(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, List[str]]:
        """_summary_

        TODO : Fully parse this, rather than just getting dictionary.

        :param raw_val: _description_
        :type raw_val: Any
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Dict[str, List[str]]
        """
        ret_val : Dict[str, List[str]]

        enums_list = LoggingSpecificationSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["enums"],
            to_type=dict,
            default_value=LoggingSpecificationSchema._DEFAULT_ENUMS,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(enums_list, dict):
            ret_val = enums_list
        else:
            ret_val = LoggingSpecificationSchema._DEFAULT_ENUMS
            Logger.Log(f"enums_list was unexpected type {type(enums_list)}, defaulting to {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _getGameState(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> GameStateSchema:
        ret_val : GameStateSchema

        game_state = LoggingSpecificationSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=[GameStateSchema, dict],
            default_value=LoggingSpecificationSchema._DEFAULT_GAME_STATE,
            remove_target=True,
            schema_name=schema_name
        )
        match game_state:
            case GameStateSchema():
                ret_val = game_state
            case dict():
                ret_val = GameStateSchema.FromDict(name="Game State", unparsed_elements=game_state)

        return ret_val

    @staticmethod
    def _getUserData(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]

        user_data = LoggingSpecificationSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["user_data"],
            to_type=dict,
            default_value=LoggingSpecificationSchema._DEFAULT_USER_DATA,
            remove_target=True,
            schema_name=schema_name
        )
        ret_val = {
            name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
            for name,elems in user_data.items()
        }

        return ret_val

    @staticmethod
    def _getEventList(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> List[EventSchema]:
        ret_val : List[EventSchema]

        events_list = LoggingSpecificationSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["events"],
            to_type=[list, dict],
            default_value=LoggingSpecificationSchema._DEFAULT_EVENT_LIST,
            remove_target=True,
            schema_name=schema_name
        )
        match events_list:
            case list():
                ret_val = [LoggingSpecificationSchema._getEvent(name=None, event=val) for val in events_list]
            case dict():
                ret_val = [
                    LoggingSpecificationSchema._getEvent(name=key, event=val) for key,val in events_list.items()
                ]

        return ret_val

    @staticmethod
    def _getEvent(name:Optional[str], event:Any) -> EventSchema:
        ret_val : EventSchema

        match event:
            case EventSchema():
                ret_val = event
            case dict():
                ret_val = EventSchema.FromDict(name=name or event.get("event_name", "UNKNOWN EVENT"), unparsed_elements=event)
            case _:
                raise TypeError(f"Logging Spec Schema raw event input was unconvertible type {type(event)}!")
        
        return ret_val

    @staticmethod
    def _getLogVersion(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> SemanticVersion:
        ret_val : SemanticVersion

        version = LoggingSpecificationSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["logging_version", "log_version"],
            to_type=[SemanticVersion, int, str],
            default_value=LoggingSpecificationSchema._DEFAULT_LOG_VERSION,
            remove_target=True,
            schema_name=schema_name
        )
        match version:
            case SemanticVersion():
                ret_val = version
            case int():
                ret_val = SemanticVersion(version)
            case str():
                ret_val = SemanticVersion.FromString(version)
            case _:
                ret_val = LoggingSpecificationSchema._DEFAULT_LOG_VERSION
        
        return ret_val

    @classmethod
    def _searchDirectories(cls, schema_name:str) -> List[str | Path]:
        """Private function that can be optionally overridden to define additional directories in which cls.Load(...) searches for a file from which to load an instance of the class.

        These extra directories are treated as optional places to search,
        and so have a lower priority than the main search paths (./, ~/, etc.)

        :return: A list of nonstandard directories in which to search for a file from which to load an instance of the class.
        :rtype: List[str | Path]
        """
        game_id = schema_name.split(".")[0] if schema_name else "UNKNOWN_GAME"
        return [cls._DEFAULT_GAME_FOLDER / game_id / "schemas"]

    # *** PRIVATE METHODS ***
