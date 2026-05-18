"""EventTableSchema Module"""
# import standard libraries
from typing import Any, Dict, List, Optional, Self

# import local files
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema, ColumnMapElement
from ogd.common.utils.typing import Map

## @class TableSchema
class EventMapSchema(ColumnMapSchema):
    """Dumb struct to hold useful info about the structure of database data for a particular game.

    This includes the indices of several important database columns, the names
    of the database columns, the max and min levels in the game, and a list of
    IDs for the game sessions in the given requested date range.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name,
                 app_id:Optional[str | List[str]],       user_id:Optional[str | List[str]],      session_id:Optional[str | List[str]],
                 app_version:Optional[ColumnMapElement], app_branch:Optional[ColumnMapElement],  log_version:Optional[ColumnMapElement],
                 timestamp:Optional[ColumnMapElement],   time_offset:Optional[ColumnMapElement], event_sequence_index:Optional[ColumnMapElement],
                 event_name:Optional[ColumnMapElement],  event_source:Optional[ColumnMapElement],event_data:Optional[ColumnMapElement],
                 game_state:Optional[ColumnMapElement],  user_data:Optional[ColumnMapElement],
                 other_elements:Optional[Map]=None):
        """Constructor for the TableSchema class.
        
        If optional params are not given, data is searched for in `other_elements`.

        The structure is assumed to be as follows:

        ```python
        {
            "session_id"           : "session_id",
            "app_id"               : null,
            "timestamp"            : "client_time",
            "event_name"           : "event_name",
            "event_data"           : "event_data",
            "event_source"         : "event_source",
            "app_version"          : "app_version",
            "app_branch"           : "app_branch",
            "log_version"          : "log_version",
            "time_offset"          : "client_offset",
            "user_id"              : "user_id",
            "user_data"            : "user_data",
            "game_state"           : "game_state",
            "event_sequence_index" : "event_sequence_index"
        }
        ```

        :param name: _description_
        :type name: _type_
        :param app_id: _description_
        :type app_id: Optional[ColumnMapElement]
        :param user_id: _description_
        :type user_id: Optional[ColumnMapElement]
        :param session_id: _description_
        :type session_id: Optional[ColumnMapElement]
        :param app_version: _description_
        :type app_version: Optional[ColumnMapElement]
        :param app_branch: _description_
        :type app_branch: Optional[ColumnMapElement]
        :param log_version: _description_
        :type log_version: Optional[ColumnMapElement]
        :param timestamp: _description_
        :type timestamp: Optional[ColumnMapElement]
        :param time_offset: _description_
        :type time_offset: Optional[ColumnMapElement]
        :param event_sequence_index: _description_
        :type event_sequence_index: Optional[ColumnMapElement]
        :param event_name: _description_
        :type event_name: Optional[ColumnMapElement]
        :param event_source: _description_
        :type event_source: Optional[ColumnMapElement]
        :param event_data: _description_
        :type event_data: Optional[ColumnMapElement]
        :param game_state: _description_
        :type game_state: Optional[ColumnMapElement]
        :param user_data: _description_
        :type user_data: Optional[ColumnMapElement]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        super().__init__(name=name, app_id=app_id, user_id=user_id, session_id=session_id,
                         other_elements=unparsed_elements)
        self._app_version          : ColumnMapElement = self._getAppVersion(raw_val=app_version, unparsed_elements=self._raw_map, schema_name=name)
        self._app_branch           : ColumnMapElement = self._getAppBranch(raw_val=app_branch, unparsed_elements=self._raw_map, schema_name=name)
        self._log_version          : ColumnMapElement = self._getLogVersion(raw_val=log_version, unparsed_elements=self._raw_map, schema_name=name)
        self._timestamp            : ColumnMapElement = self._getTimestamp(raw_val=timestamp, unparsed_elements=unparsed_elements, schema_name=name)
        self._time_offset          : ColumnMapElement = self._getTimeoffset(raw_val=time_offset, unparsed_elements=unparsed_elements, schema_name=name)
        self._event_sequence_index : ColumnMapElement = self._getSequenceIndex(raw_val=event_sequence_index, unparsed_elements=unparsed_elements, schema_name=name)
        self._event_name           : ColumnMapElement = self._getEventName(raw_val=event_name, unparsed_elements=unparsed_elements, schema_name=name)
        self._event_source         : ColumnMapElement = self._getEventSource(raw_val=event_source, unparsed_elements=unparsed_elements, schema_name=name)
        self._event_data           : ColumnMapElement = self._getEventData(raw_val=event_data, unparsed_elements=unparsed_elements, schema_name=name)
        self._game_state           : ColumnMapElement = self._getGameState(raw_val=game_state, unparsed_elements=unparsed_elements, schema_name=name)
        self._user_data            : ColumnMapElement = self._getUserData(raw_val=user_data, unparsed_elements=unparsed_elements, schema_name=name)

    def __eq__(self, other:"EventMapSchema"):
        if not isinstance(other, EventMapSchema):
            return False
        else:
            return self.AppIDColumn == other.AppIDColumn \
               and self.UserIDColumn == other.UserIDColumn \
               and self.SessionIDColumn == other.SessionIDColumn \
               and self.AppVersionColumn == other.AppVersionColumn \
               and self.AppBranchColumn == other.AppBranchColumn \
               and self.LogVersionColumn == other.LogVersionColumn \
               and self.TimestampColumn == other.TimestampColumn \
               and self.TimeOffsetColumn == other.TimeOffsetColumn \
               and self.EventSequenceIndexColumn == other.EventSequenceIndexColumn \
               and self.EventNameColumn == other.EventNameColumn \
               and self.EventSourceColumn == other.EventSourceColumn \
               and self.EventDataColumn == other.EventDataColumn \
               and self.GameStateColumn == other.GameStateColumn \
               and self.UserDataColumn == other.UserDataColumn

    @property
    def AppVersionColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to AppVersion

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._app_version

    @property
    def AppBranchColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to AppBranch

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._app_branch

    @property
    def LogVersionColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to LogVersion

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._log_version

    @property
    def TimestampColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to Timestamp

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._timestamp

    @property
    def EventNameColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to EventName

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._event_name

    @property
    def EventDataColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to EventData

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._event_data

    @property
    def EventSourceColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to EventSource

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._event_source

    @property
    def TimeOffsetColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to TimeOffset

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._time_offset

    @property
    def UserDataColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to UserData

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._user_data

    @property
    def GameStateColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to GameState

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._game_state

    @property
    def EventSequenceIndexColumn(self) -> ColumnMapElement:
        """The column(s) of the storage table that is/are mapped to Event Sequence Index

        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        return self._event_sequence_index

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsDict(self) -> Dict[str, Any]:
        return {
            "app_id":self.AppIDColumn,
            "user_id":self.UserIDColumn,
            "session_id":self.SessionIDColumn,
            "app_version":self.AppVersionColumn,
            "app_branch":self.AppBranchColumn,
            "log_version":self.LogVersionColumn,
            "timestamp":self.TimestampColumn,
            "offset":self.TimeOffsetColumn,
            "event_sequence_index":self.EventSequenceIndexColumn,
            "event_name":self.EventNameColumn,
            "event_source":self.EventSourceColumn,
            "event_data":self.EventDataColumn,
            "game_state":self.GameStateColumn,
            "user_data":self.UserDataColumn
        }

    @classmethod
    def Default(cls) -> "EventMapSchema":
        return EventMapSchema(
            name="DefaultEventTableSchema",
            app_id="app_id",
            user_id="user_id",
            session_id="session_id",
            app_version="app_version",
            app_branch="app_branch",
            log_version="log_version",
            timestamp="timestamp",
            time_offset="time_offset",
            event_sequence_index="event_sequence_index",
            event_name="event_name",
            event_source="event_source",
            event_data="event_data",
            game_state="game_state",
            user_data="user_data",
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "EventMapSchema":
        """Function to generate an EventMapSchema from a dictionary.

        The structure is assumed to be as follows:
        ```python
        {
            "session_id"           : "session_id",
            "app_id"               : null,
            "timestamp"            : "client_time",
            "event_name"           : "event_name",
            "event_data"           : "event_data",
            "event_source"         : "event_source",
            "app_version"          : "app_version",
            "app_branch"           : "app_branch",
            "log_version"          : "log_version",
            "time_offset"          : "client_offset",
            "user_id"              : "user_id",
            "user_data"            : "user_data",
            "game_state"           : "game_state",
            "event_sequence_index" : "event_sequence_index"
        }
        ```

        The specific handling of the column map will be determined by the specific TableSchema subclass on which the FromDict feature is called.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :param key_overrides: _description_, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :param default_override: _description_, defaults to None
        :type default_override: Optional[Self], optional
        :return: _description_
        :rtype: EventMapSchema
        """
        return EventMapSchema(name=name,
                              app_id=None, user_id=None, session_id=None,
                              app_version=None, app_branch=None, log_version=None,
                              timestamp=None, time_offset=None, event_sequence_index=None,
                              event_name=None, event_source=None, event_data=None,
                              game_state=None, user_data=None,
                              other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _getAppVersion(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["app_version"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getAppBranch(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["app_branch", "app_flavor"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getLogVersion(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["log_version"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getTimestamp(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["timestamp"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getTimeoffset(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["offset", "time_offset", "timezone", "time_zone"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getSequenceIndex(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["event_sequence_index", "event_index", "sequence_index"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getEventName(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["event_name", "event_type"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getEventSource(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["event_source", "source"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getEventData(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["event_data"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getGameState(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )

    @staticmethod
    def _getUserData(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["user_data", "player_data"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False,
            schema_name=schema_name
        )
