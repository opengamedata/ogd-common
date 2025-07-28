"""EventTableSchema Module"""
# import standard libraries
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple, Optional

# import local files
from ogd.common.schemas.tables.TableSchema import ColumnMapElement, ColumnMapElement
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.utils.Logger import Logger
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
                 app_id:Optional[ColumnMapElement],      user_id:Optional[ColumnMapElement],     session_id:Optional[ColumnMapElement],
                 app_version:Optional[ColumnMapElement], app_branch:Optional[ColumnMapElement],  log_version:Optional[ColumnMapElement],
                 timestamp:Optional[ColumnMapElement],   time_offset:Optional[ColumnMapElement], event_sequence_index:Optional[ColumnMapElement],
                 event_name:Optional[ColumnMapElement],  event_source:Optional[ColumnMapElement],event_data:Optional[ColumnMapElement],
                 game_state:Optional[ColumnMapElement],  user_data:Optional[ColumnMapElement],
                 other_elements:Optional[Map]=None):
        """Constructor for the TableSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        unparsed_elements : Map = other_elements or {}

        self._timestamp            : ColumnMapElement = timestamp            or self._parseTimestamp(unparsed_elements=unparsed_elements)
        self._time_offset          : ColumnMapElement = time_offset          or self._parseTimeoffset(unparsed_elements=unparsed_elements)
        self._event_sequence_index : ColumnMapElement = event_sequence_index or self._parseSequenceIndex(unparsed_elements=unparsed_elements)
        self._event_name           : ColumnMapElement = event_name           or self._parseEventName(unparsed_elements=unparsed_elements)
        self._event_source         : ColumnMapElement = event_source         or self._parseEventSource(unparsed_elements=unparsed_elements)
        self._event_data           : ColumnMapElement = event_data           or self._parseEventData(unparsed_elements=unparsed_elements)
        self._game_state           : ColumnMapElement = game_state           or self._parseGameState(unparsed_elements=unparsed_elements)
        self._user_data            : ColumnMapElement = user_data            or self._parseUserData(unparsed_elements=unparsed_elements)

        super().__init__(name=name, app_id=app_id, user_id=user_id, session_id=session_id,
                         app_version=app_version, app_branch=app_branch, log_version=log_version,
                         other_elements=unparsed_elements)

    @property
    def TimestampColumn(self) -> ColumnMapElement:
        return self._timestamp

    @property
    def EventNameColumn(self) -> ColumnMapElement:
        return self._event_name

    @property
    def EventDataColumn(self) -> ColumnMapElement:
        return self._event_data

    @property
    def EventSourceColumn(self) -> ColumnMapElement:
        return self._event_source

    @property
    def TimeOffsetColumn(self) -> ColumnMapElement:
        return self._time_offset

    @property
    def UserDataColumn(self) -> ColumnMapElement:
        return self._user_data

    @property
    def GameStateColumn(self) -> ColumnMapElement:
        return self._game_state

    @property
    def EventSequenceIndexColumn(self) -> ColumnMapElement:
        return self._event_sequence_index

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def Default(cls) -> "EventMapSchema":
        return EventMapSchema(
            name="DefaultEventTableSchema",
            column_map={},
            columns=cls._DEFAULT_COLUMNS,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseTimestamp(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["timestamp"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseTimeoffset(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["offset", "time_offset", "timezone", "time_zone"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseSequenceIndex(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_sequence_index", "event_index", "sequence_index"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseEventName(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_name", "event_type"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseEventSource(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_source", "source"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseEventData(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_data"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseGameState(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseUserData(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["user_data", "player_data"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )
