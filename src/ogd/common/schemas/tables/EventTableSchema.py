"""EventTableSchema Module"""
# import standard libraries
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple, Optional

# import local files
from ogd.common.models.enums.TableType import TableType
from ogd.common.models.Event import Event, EventSource
from ogd.common.schemas.tables.TableSchema import TableSchema, ColumnMapIndex, ColumnMapElement
from ogd.common.utils import utils
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

## @class TableSchema
#  Dumb struct to hold useful info about the structure of database data
#  for a particular game.
#  This includes the indices of several important database columns, the names
#  of the database columns, the max and min levels in the game, and a list of
#  IDs for the game sessions in the given requested date range.
class EventTableSchema(TableSchema):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name, table_type:TableType, column_map:Dict[str, ColumnMapIndex], columns:List[ColumnSchema]):
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
        super().__init__(name=name, table_type=table_type, column_map=column_map, columns=columns)

    @property
    def SessionIDIndex(self) -> ColumnMapIndex:
        return self._column_map['session_id']

    @property
    def AppIDIndex(self) -> ColumnMapIndex:
        return self._column_map['app_id']

    @property
    def TimestampIndex(self) -> ColumnMapIndex:
        return self._column_map['timestamp']

    @property
    def EventNameIndex(self) -> ColumnMapIndex:
        return self._column_map['event_name']

    @property
    def EventDataIndex(self) -> ColumnMapIndex:
        return self._column_map['event_data']

    @property
    def EventSourceIndex(self) -> ColumnMapIndex:
        return self._column_map['event_source']

    @property
    def AppVersionIndex(self) -> ColumnMapIndex:
        return self._column_map['app_version']

    @property
    def AppBranchIndex(self) -> ColumnMapIndex:
        return self._column_map['app_branch']

    @property
    def LogVersionIndex(self) -> ColumnMapIndex:
        return self._column_map['log_version']

    @property
    def TimeOffsetIndex(self) -> ColumnMapIndex:
        return self._column_map['time_offset']

    @property
    def UserIDIndex(self) -> ColumnMapIndex:
        return self._column_map['user_id']

    @property
    def UserDataIndex(self) -> ColumnMapIndex:
        return self._column_map['user_data']

    @property
    def GameStateIndex(self) -> ColumnMapIndex:
        return self._column_map['game_state']

    @property
    def EventSequenceIndexIndex(self) -> ColumnMapIndex:
        return self._column_map['event_sequence_index']

    @property
    def SessionIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.SessionIDIndex, int):
            ret_val = self.ColumnNames[self.SessionIDIndex]
        elif isinstance(self.SessionIDIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.SessionIDIndex])
        return ret_val

    @property
    def AppIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.AppIDIndex, int):
            ret_val = self.ColumnNames[self.AppIDIndex]
        elif isinstance(self.AppIDIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.AppIDIndex])
        return ret_val

    @property
    def TimestampColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.TimestampIndex, int):
            ret_val = self.ColumnNames[self.TimestampIndex]
        elif isinstance(self.TimestampIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.TimestampIndex])
        return ret_val

    @property
    def EventNameColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.EventNameIndex, int):
            ret_val = self.ColumnNames[self.EventNameIndex]
        elif isinstance(self.EventNameIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.EventNameIndex])
        return ret_val

    @property
    def EventDataColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.EventDataIndex, int):
            ret_val = self.ColumnNames[self.EventDataIndex]
        elif isinstance(self.EventDataIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.EventDataIndex])
        return ret_val

    @property
    def EventSourceColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.EventSourceIndex, int):
            ret_val = self.ColumnNames[self.EventSourceIndex]
        elif isinstance(self.EventSourceIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.EventSourceIndex])
        return ret_val

    @property
    def AppVersionColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.AppVersionIndex, int):
            ret_val = self.ColumnNames[self.AppVersionIndex]
        elif isinstance(self.AppVersionIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.AppVersionIndex])
        return ret_val

    @property
    def AppBranchColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.AppBranchIndex, int):
            ret_val = self.ColumnNames[self.AppBranchIndex]
        elif isinstance(self.AppBranchIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.AppBranchIndex])
        return ret_val

    @property
    def LogVersionColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.LogVersionIndex, int):
            ret_val = self.ColumnNames[self.LogVersionIndex]
        elif isinstance(self.LogVersionIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.LogVersionIndex])
        return ret_val

    @property
    def TimeOffsetColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.TimeOffsetIndex, int):
            ret_val = self.ColumnNames[self.TimeOffsetIndex]
        elif isinstance(self.TimeOffsetIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.TimeOffsetIndex])
        return ret_val

    @property
    def UserIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.UserIDIndex, int):
            ret_val = self.ColumnNames[self.UserIDIndex]
        elif isinstance(self.UserIDIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.UserIDIndex])
        return ret_val

    @property
    def UserDataColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.UserDataIndex, int):
            ret_val = self.ColumnNames[self.UserDataIndex]
        elif isinstance(self.UserDataIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.UserDataIndex])
        return ret_val

    @property
    def GameStateColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.GameStateIndex, int):
            ret_val = self.ColumnNames[self.GameStateIndex]
        elif isinstance(self.GameStateIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.GameStateIndex])
        return ret_val

    @property
    def EventSequenceIndexColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.EventSequenceIndexIndex, int):
            ret_val = self.ColumnNames[self.EventSequenceIndexIndex]
        elif isinstance(self.EventSequenceIndexIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.EventSequenceIndexIndex])
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _fromDict(cls, name:str, table_type:TableType, raw_map:Dict[str, ColumnMapElement], column_schemas:List[ColumnSchema]) -> "TableSchema":
        _column_map : Dict[str, ColumnMapIndex] = {}
        return EventTableSchema(name=name, table_type=table_type, column_map=_column_map, columns=column_schemas)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    _conversion_warnings = []
    def RowToEvent(self, row:Tuple, concatenator:str = '.', fallbacks:Map={}):
        """Function to convert a row to an Event, based on the loaded schema.
        In general, columns specified in the schema's column_map are mapped to corresponding elements of the Event.
        If the column_map gave a list, rather than a single column name, the values from each column are concatenated in order with '.' character separators.
        Finally, the concatenated values (or single value) are parsed according to the type required by Event.
        One exception: For event_data, we expect to create a Dict object, so each column in the list will have its value parsed according to the type in 'columns',
            and placed into a dict mapping the original column name to the parsed value (unless the parsed value is a dict, then it is merged into the top-level dict).

        :param row: The raw row data for an event. Generally assumed to be a tuple, though in principle a list would be fine too.
        :type  row: Tuple[str]
        :param concatenator: A string to use as a separator when concatenating multiple columns into a single Event element.
        :type  concatenator: str
        :return: [description]
        :rtype: [type]
        """
        # define vars to be passed as params
        sess_id : str
        app_id  : str
        tstamp  : datetime
        ename   : str
        edata   : Map
        app_ver : str
        app_br  : str
        log_ver : str
        offset  : Optional[timezone]
        uid     : Optional[str]
        udata   : Optional[Map]
        state   : Optional[Map]
        index   : Optional[int]

        # 2) Handle event_data parameter, a special case.
        #    For this case we've got to parse the json, and then fold in whatever other columns were desired.
        # 3) Assign vals to our arg vars and pass to Event ctor.
        sess_id = self._getValueFromRow(row=row, indices=self.SessionIDIndex,   concatenator=concatenator, fallback=fallbacks.get('session_id'))
        if not isinstance(sess_id, str):
            if "sess_id" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set session_id as {type(sess_id)}, but session_id should be a string", logging.WARN)
                EventTableSchema._conversion_warnings.append("sess_id")
            sess_id = str(sess_id)

        app_id  = self._getValueFromRow(row=row, indices=self.AppIDIndex,       concatenator=concatenator, fallback=fallbacks.get('app_id'))
        if not isinstance(app_id, str):
            if "app_id" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set app_id as {type(app_id)}, but app_id should be a string", logging.WARN)
                EventTableSchema._conversion_warnings.append("app_id")
            app_id = str(app_id)

        tstamp  = self._getValueFromRow(row=row, indices=self.TimestampIndex,   concatenator=concatenator, fallback=fallbacks.get('timestamp'))
        if not isinstance(tstamp, datetime):
            if "timestamp" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema parsed timestamp as {type(tstamp)}, but timestamp should be a datetime", logging.WARN)
                EventTableSchema._conversion_warnings.append("timestamp")
            tstamp = conversions.DatetimeFromString(tstamp)

        ename   = self._getValueFromRow(row=row, indices=self.EventNameIndex,   concatenator=concatenator, fallback=fallbacks.get('event_name'))
        if not isinstance(ename, str):
            if "ename" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set event_name as {type(ename)}, but event_name should be a string", logging.WARN)
                EventTableSchema._conversion_warnings.append("ename")
            ename = str(ename)

        datas : Dict[str, Any] = self._getValueFromRow(row=row, indices=self.EventDataIndex,   concatenator=concatenator, fallback=fallbacks.get('event_data'))

        # TODO: go bac to isostring function; need 0-padding on ms first, though
        edata   = dict(sorted(datas.items())) # Sort keys alphabetically

        esrc    = self._getValueFromRow(row=row, indices=self.EventSourceIndex, concatenator=concatenator, fallback=fallbacks.get('event_source', EventSource.GAME))
        if not isinstance(esrc, EventSource):
            if "esrc" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set event_source as {type(esrc)}, but event_source should be an EventSource", logging.WARN)
                EventTableSchema._conversion_warnings.append("esrc")
            esrc = EventSource.GENERATED if esrc == "GENERATED" else EventSource.GAME

        app_ver = self._getValueFromRow(row=row, indices=self.AppVersionIndex,  concatenator=concatenator, fallback=fallbacks.get('app_version', "0"))
        if not isinstance(app_ver, str):
            if "app_ver" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set app_version as {type(app_ver)}, but app_version should be a string", logging.WARN)
                EventTableSchema._conversion_warnings.append("app_ver")
            app_ver = str(app_ver)

        app_br = self._getValueFromRow(row=row, indices=self.AppBranchIndex,  concatenator=concatenator, fallback=fallbacks.get('app_branch'))
        if not isinstance(app_br, str):
            if "app_br" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set app_branch as {type(app_br)}, but app_branch should be a string", logging.WARN)
                EventTableSchema._conversion_warnings.append("app_br")
            app_br = str(app_br)

        log_ver = self._getValueFromRow(row=row, indices=self.LogVersionIndex,  concatenator=concatenator, fallback=fallbacks.get('log_version', "0"))
        if not isinstance(log_ver, str):
            if "log_ver" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set log_version as {type(log_ver)}, but log_version should be a string", logging.WARN)
                EventTableSchema._conversion_warnings.append("log_ver")
            log_ver = str(log_ver)

        offset = self._getValueFromRow(row=row, indices=self.TimeOffsetIndex,  concatenator=concatenator, fallback=fallbacks.get('time_offset'))
        if isinstance(offset, timedelta):
            if "offset" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set offset as {type(offset)}, but offset should be a timezone", logging.WARN)
                EventTableSchema._conversion_warnings.append("offset")
            offset = timezone(offset)

        uid     = self._getValueFromRow(row=row, indices=self.UserIDIndex,      concatenator=concatenator, fallback=fallbacks.get('user_id'))
        if uid is not None and not isinstance(uid, str):
            if "uid" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set user_id as {type(uid)}, but user_id should be a string", logging.WARN)
                EventTableSchema._conversion_warnings.append("uid")
            uid = str(uid)

        udata   = self._getValueFromRow(row=row, indices=self.UserDataIndex,    concatenator=concatenator, fallback=fallbacks.get('user_data'))

        state   = self._getValueFromRow(row=row, indices=self.GameStateIndex,   concatenator=concatenator, fallback=fallbacks.get('game_state'))

        index   = self._getValueFromRow(row=row, indices=self.EventSequenceIndexIndex, concatenator=concatenator, fallback=fallbacks.get('event_sequence_index'))
        if index is not None and not isinstance(index, int):
            if "index" not in EventTableSchema._conversion_warnings:
                Logger.Log(f"{self.Name} {self.TableKind} table schema set event_sequence_index as {type(index)}, but event_sequence_index should be an int", logging.WARN)
                EventTableSchema._conversion_warnings.append("index")
            index = int(index)

        return Event(session_id=sess_id, app_id=app_id, timestamp=tstamp,
                     event_name=ename, event_data=edata, event_source=esrc,
                     app_version=app_ver, app_branch=app_br, log_version=log_ver,
                     time_offset=offset, user_id=uid, user_data=udata,
                     game_state=state, event_sequence_index=index)

    # *** PRIVATE STATICS ***
