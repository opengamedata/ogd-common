"""EventTableSchema Module"""
# import standard libraries
import logging
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple, Optional

# import local files
from ogd.common.models.Feature import Feature
from ogd.common.models.Event import EventSource
from ogd.common.schemas.tables.TableSchema import TableSchema, ColumnMapElement, ColumnMapElement
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

## @class TableSchema
class FeatureMapSchema(TableSchema):
    """Dumb struct to hold useful info about the structure of feature data for a particular game in a particular database.
       This includes the indices of several important database columns, the names
       of the database columns, and a list of
       IDs for the game sessions in the given requested date range.

       TODO : right now, this is all just a copy of what's in EventTableSchema, need to implement for feature data.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name, column_map:Dict[str, ColumnMapElement], columns:List[ColumnSchema], other_elements:Optional[Map]=None):
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
        super().__init__(name=name, column_map=column_map, columns=columns, other_elements=other_elements)

    @property
    def TimestampIndex(self) -> ColumnMapElement:
        return self._column_map['timestamp']

    @property
    def EventNameIndex(self) -> ColumnMapElement:
        return self._column_map['event_name']

    @property
    def EventDataIndex(self) -> ColumnMapElement:
        return self._column_map['event_data']

    @property
    def EventSourceIndex(self) -> ColumnMapElement:
        return self._column_map['event_source']

    @property
    def TimeOffsetIndex(self) -> ColumnMapElement:
        return self._column_map['time_offset']

    @property
    def UserDataIndex(self) -> ColumnMapElement:
        return self._column_map['user_data']

    @property
    def GameStateIndex(self) -> ColumnMapElement:
        return self._column_map['game_state']

    @property
    def EventSequenceIndexIndex(self) -> ColumnMapElement:
        return self._column_map['event_sequence_index']

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
    def TimeOffsetColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.TimeOffsetIndex, int):
            ret_val = self.ColumnNames[self.TimeOffsetIndex]
        elif isinstance(self.TimeOffsetIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.TimeOffsetIndex])
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

    @property
    def AsMarkdown(self) -> str:
        ret_val = "\n\n".join([
            "## Database Columns",
            "The individual columns recorded in the database for this game.",
            self._columnSetMarkdown,
            "## Feature Object Elements",
            "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.",
            self._columnMapMarkdown,
            ""])
        return ret_val

    @classmethod
    def Default(cls) -> "FeatureMapSchema":
        return FeatureMapSchema(
            name="DefaultFeatureTableSchema",
            column_map={},
            columns=cls._DEFAULT_COLUMNS,
            other_elements={}
        )

    @classmethod
    def _subparseDict(cls, name:str, raw_map:Dict[str, ColumnMapElement], column_schemas:List[ColumnSchema], logger:Optional[logging.Logger]=None) -> "TableSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param raw_map: _description_
        :type raw_map: Dict[str, ColumnMapElement]
        :param column_schemas: _description_
        :type column_schemas: List[ColumnSchema]
        :param logger: _description_, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: _description_
        :rtype: TableSchema
        """
        _column_map : Dict[str, ColumnMapElement] = {
            "session_id"           : None,
            "app_id"               : None,
            "timestamp"            : None,
            "event_name"           : None,
            "event_data"           : None,
            "event_source"         : None,
            "app_version"          : None,
            "app_branch"           : None,
            "log_version"          : None,
            "time_offset"          : None,
            "user_id"              : None,
            "user_data"            : None,
            "game_state"           : None,
            "event_sequence_index" : None
        }

        column_names = [elem.Name for elem in column_schemas]
        if not isinstance(raw_map, dict):
            raw_map = {}
            _msg = f"For {name} column map schema, raw_map was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        # for each item in the map above that we expect...
        for key in _column_map.keys():
            # if the item was found in the given "column_map" dictionary...
            if key in raw_map:
                # parse what was mapped to the item. Could get back a string, or a list, or a dict...
                element = cls._retrieveElement(elem=map[key], name=key)
                # then if we got a string, we just find it in list of column names
                if isinstance(element, str):
                    _column_map[key] = column_names.index(element)
                # but if it's a list, we need to get index of each item in list of column names
                elif isinstance(element, list):
                    _column_map[key] = [column_names.index(listelem) for listelem in element]
                # but if it's a dict, we need to make equivalent dict mapping the key (new name) to the index (in list of column names)
                elif isinstance(element, dict):
                    _column_map[key] = {key : column_names.index(listelem) for key,listelem in element.items()}
            else:
                Logger.Log(f"Column config does not have a '{key}' element, defaulting to {key} : None", logging.WARN)
        _leftovers = { key : val for key,val in raw_map.items() if key not in _column_map.keys() }

        return FeatureMapSchema(name=name, column_map=_column_map, columns=column_schemas, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    _conversion_warnings = Counter()
    def RowToFeature(self, row:Tuple, concatenator:str = '.', fallbacks:Map={}) -> Feature:
        """Function to convert a row to a Feature value, based on the loaded schema.
        In general, columns specified in the schema's column_map are mapped to corresponding elements of the Event.
        If the column_map gave a list, rather than a single column name, the values from each column are concatenated in order with '.' character separators.
        Finally, the concatenated values (or single value) are parsed according to the type required by Event.
        One exception: For event_data, we expect to create a Dict object, so each column in the list will have its value parsed according to the type in 'columns',
            and placed into a dict mapping the original column name to the parsed value (unless the parsed value is a dict, then it is merged into the top-level dict).

        TODO : actually implement this whole dang function.

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
        sess_id = self._valueFromRow(row=row, indices=self.SessionIDIndex,   concatenator=concatenator, fallback=fallbacks.get('session_id'))
        if not isinstance(sess_id, str):
            if "sess_id" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set session_id as {type(sess_id)}, but session_id should be a string", logging.WARN)
            FeatureMapSchema._conversion_warnings["sess_id"] += 1
            sess_id = str(sess_id)

        app_id  = self._valueFromRow(row=row, indices=self.AppIDIndex,       concatenator=concatenator, fallback=fallbacks.get('app_id'))
        if not isinstance(app_id, str):
            if "app_id" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set app_id as {type(app_id)}, but app_id should be a string", logging.WARN)
            FeatureMapSchema._conversion_warnings["app_id"] += 1
            app_id = str(app_id)

        tstamp  = self._valueFromRow(row=row, indices=self.TimestampIndex,   concatenator=concatenator, fallback=fallbacks.get('timestamp'))
        if not isinstance(tstamp, datetime):
            if "timestamp" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema parsed timestamp as {type(tstamp)}, but timestamp should be a datetime", logging.WARN)
            FeatureMapSchema._conversion_warnings["timestamp"] += 1
            tstamp = conversions.DatetimeFromString(tstamp)

        ename   = self._valueFromRow(row=row, indices=self.EventNameIndex,   concatenator=concatenator, fallback=fallbacks.get('event_name'))
        if not isinstance(ename, str):
            if "ename" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set event_name as {type(ename)}, but event_name should be a string", logging.WARN)
            FeatureMapSchema._conversion_warnings["ename"] += 1
            ename = str(ename)

        datas : Dict[str, Any] = self._valueFromRow(row=row, indices=self.EventDataIndex,   concatenator=concatenator, fallback=fallbacks.get('event_data'))

        # TODO: go bac to isostring function; need 0-padding on ms first, though
        edata   = dict(sorted(datas.items())) # Sort keys alphabetically

        esrc    = self._valueFromRow(row=row, indices=self.EventSourceIndex, concatenator=concatenator, fallback=fallbacks.get('event_source', EventSource.GAME))
        if not isinstance(esrc, EventSource):
            if "esrc" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set event_source as {type(esrc)}, but event_source should be an EventSource", logging.WARN)
            FeatureMapSchema._conversion_warnings["esrc"] += 1
            esrc = EventSource.GENERATED if esrc == "GENERATED" else EventSource.GAME

        app_ver = self._valueFromRow(row=row, indices=self.AppVersionIndex,  concatenator=concatenator, fallback=fallbacks.get('app_version', "0"))
        if not isinstance(app_ver, str):
            if "app_ver" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set app_version as {type(app_ver)}, but app_version should be a string", logging.WARN)
            FeatureMapSchema._conversion_warnings["app_ver"] += 1
            app_ver = str(app_ver)

        app_br = self._valueFromRow(row=row, indices=self.AppBranchIndex,  concatenator=concatenator, fallback=fallbacks.get('app_branch'))
        if not isinstance(app_br, str):
            if "app_br" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set app_branch as {type(app_br)}, but app_branch should be a string", logging.WARN)
            FeatureMapSchema._conversion_warnings["app_br"] += 1
            app_br = str(app_br)

        log_ver = self._valueFromRow(row=row, indices=self.LogVersionIndex,  concatenator=concatenator, fallback=fallbacks.get('log_version', "0"))
        if not isinstance(log_ver, str):
            if "log_ver" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set log_version as {type(log_ver)}, but log_version should be a string", logging.WARN)
            FeatureMapSchema._conversion_warnings["log_ver"] += 1
            log_ver = str(log_ver)

        offset = self._valueFromRow(row=row, indices=self.TimeOffsetIndex,  concatenator=concatenator, fallback=fallbacks.get('time_offset'))
        if isinstance(offset, timedelta):
            if "offset" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set offset as {type(offset)}, but offset should be a timezone", logging.WARN)
            FeatureMapSchema._conversion_warnings["offset"] += 1
            offset = timezone(offset)

        uid     = self._valueFromRow(row=row, indices=self.UserIDIndex,      concatenator=concatenator, fallback=fallbacks.get('user_id'))
        if uid is not None and not isinstance(uid, str):
            if "uid" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set user_id as {type(uid)}, but user_id should be a string", logging.WARN)
            FeatureMapSchema._conversion_warnings["uid"] += 1
            uid = str(uid)

        udata   = self._valueFromRow(row=row, indices=self.UserDataIndex,    concatenator=concatenator, fallback=fallbacks.get('user_data'))

        state   = self._valueFromRow(row=row, indices=self.GameStateIndex,   concatenator=concatenator, fallback=fallbacks.get('game_state'))

        index   = self._valueFromRow(row=row, indices=self.EventSequenceIndexIndex, concatenator=concatenator, fallback=fallbacks.get('event_sequence_index'))
        if index is not None and not isinstance(index, int):
            if "index" not in FeatureMapSchema._conversion_warnings:
                Logger.Log(f"{self.Name} feature table schema set event_sequence_index as {type(index)}, but event_sequence_index should be an int", logging.WARN)
            FeatureMapSchema._conversion_warnings["index"] += 1
            index = int(index)

        return Feature(name="FeaturesNotImplemented", feature_type="FeaturesNotImplemented", count_index=None,
                           cols=[], vals=[], mode=ExtractionMode.SESSION, app_id="NONE", user_id=None, session_id="NONE",
                           app_version=None, app_branch=None, log_version=None
                           )

    # *** PRIVATE STATICS ***
