## import standard libraries
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Final, List, Tuple, Optional, Union
## import 3rd-party libraries
from dateutil import parser
## import local files
from ogd.common import schemas
from ogd.common.models.Event import Event, EventSource
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.utils import utils
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class TableSchema
class TableSchema(Schema):
    """Dumb struct to hold info about the structure of data for a particular game, from a particular source.
        In particular, it contains an ordered list of columns in the data source table,
        and a mapping of those columns to the corresponding elements of a formal OGD structure.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name, column_map:ColumnMapSchema, columns:List[ColumnSchema]):
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
        # declare and initialize vars
        # self._schema            : Optional[Dict[str, Any]] = all_elements
        self._column_map        : ColumnMapSchema    = column_map
        self._table_columns     : List[ColumnSchema] = columns

        # after loading the file, take the stuff we need and store.
        super().__init__(name=name, other_elements={})

    @property
    def ColumnNames(self) -> List[str]:
        """Function to get the names of all columns in the schema.

        :return: Names of each column in the schema.
        :rtype: List[str]
        """
        return [col.Name for col in self._table_columns]

    @property
    def Columns(self) -> List[ColumnSchema]:
        return self._table_columns

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # @classmethod
    # def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "TableSchema":
    #     _column_map     : ColumnMapSchema
    #     _column_schemas : List[ColumnSchema]

    #     if not isinstance(all_elements, dict):
    #         all_elements = {}
    #         _msg = f"For {name} Table Schema, all_elements was not a dict, defaulting to empty dict"
    #         if logger:
    #             logger.warning(_msg)
    #         else:
    #             Logger.Log(_msg, logging.WARN)
    #     _column_json_list = all_elements.get('columns', [])
    #     _column_schemas   = [ColumnSchema.FromDict(name=column.get("name", "UNKNOWN COLUMN NAME"), all_elements=column) for column in _column_json_list]
    #     _column_map       = ColumnMapSchema.FromDict(name="Column Map", all_elements=all_elements.get('column_map', {}), column_names=[col.Name for col in _column_schemas])
    #     return TableSchema(name=name, column_map=_column_map, columns=_column_schemas)

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(schema_name:str, schema_path:Path = Path(schemas.__file__).parent / "table_schemas/") -> "TableSchema":
        _table_format_name : str = schema_name

        if not _table_format_name.lower().endswith(".json"):
            _table_format_name += ".json"
        _schema = utils.loadJSONFile(filename=_table_format_name, path=schema_path)

        return TableSchema.FromDict(name=schema_name, all_elements=_schema)

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parse(input:Any, col_schema:ColumnSchema) -> Any:
        """Applies whatever parsing is appropriate based on what type the schema said a column contained.

        :param input: _description_
        :type input: str
        :param col_schema: _description_
        :type col_schema: ColumnSchema
        :return: _description_
        :rtype: Any
        """
        if input is None:
            return None
        if input == "None" or input == "null" or input == "nan":
            return None
        match col_schema.ValueType.upper():
            case 'STR':
                return str(input)
            case 'INT':
                return int(input)
            case 'FLOAT':
                return float(input)
            case 'DATETIME':
                return input if isinstance(input, datetime) else TableSchema._convertDateTime(str(input))
            case 'TIMEDELTA':
                return input if isinstance(input, timedelta) else TableSchema._convertTimedelta(str(input))
            case 'TIMEZONE':
                return input if isinstance(input, timezone) else TableSchema._convertTimezone(str(input))
            case 'JSON':
                try:
                    if isinstance(input, dict):
                        # if input was a dict already, then just give it back. Else, try to load it from string.
                        return input
                    elif isinstance(input, str):
                        if input != 'None' and input != '': # watch out for nasty corner cases.
                            return json.loads(input)
                        else:
                            return None
                    else:
                        return json.loads(str(input))
                except JSONDecodeError as err:
                    Logger.Log(f"Could not parse input '{input}' of type {type(input)} from column {col_schema.Name}, got the following error:\n{str(err)}", logging.WARN)
                    return {}
            case _dummy if _dummy.startswith('ENUM'):
                # if the column is supposed to be an enum, for now we just stick with the string.
                return str(input)
            case _:
                Logger.Log(f"_parse function got an unrecognized column type {col_schema.ValueType}, could not parse!", logging.WARNING)

    @staticmethod
    def _convertDateTime(time_str:str) -> datetime:
        ret_val : datetime

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            raise ValueError(f"Got a non-timestamp value of {time_str} when converting a datetime column from data source!")

        formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S.%f"]

        try:
            ret_val = parser.isoparse(time_str)
        except ValueError:
            # Logger.Log(f"Could not parse time string '{time_str}', got error {err}")
            # raise err
            pass
        else:
            return ret_val
        for fmt in formats:
            try:
                ret_val = datetime.strptime(time_str, fmt)
            except ValueError:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timestamp {time_str}, it did not match any expected formats!")

    @staticmethod
    def _convertTimedelta(time_str:str) -> Optional[timedelta]:
        ret_val : Optional[timedelta]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"\d+:\d+:\d+(\.\d+)?", string=time_str):
            try:
                pieces = time_str.split(':')
                seconds_pieces = pieces[2].split('.')
                ret_val = timedelta(hours=int(pieces[0]),
                                    minutes=int(pieces[1]),
                                    seconds=int(seconds_pieces[0]),
                                    milliseconds=int(seconds_pieces[1]) if len(seconds_pieces) > 1 else 0)
            except ValueError as err:
                pass
            except IndexError as err:
                pass
            else:
                return ret_val
        elif re.fullmatch(pattern=r"-?\d+", string=time_str):
            try:
                ret_val = timedelta(seconds=int(time_str))
            except ValueError as err:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timedelta {time_str} of type {type(time_str)}, it did not match any expected formats.")

    @staticmethod
    def _convertTimezone(time_str:str) -> Optional[timezone]:
        ret_val : Optional[timezone]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"UTC[+-]\d+:\d+", string=time_str):
            try:
                pieces = time_str.removeprefix("UTC").split(":")
                ret_val = timezone(timedelta(hours=int(pieces[0]), minutes=int(pieces[1])))
            except ValueError as err:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timezone {time_str} of type {type(time_str)}, it did not match any expected formats.")

    # *** PRIVATE METHODS ***

    def _getValueFromRow(self, row:Tuple, indices:Union[int, List[int], Dict[str, int], None], concatenator:str, fallback:Any) -> Any:
        ret_val : Any
        if indices is not None:
            if isinstance(indices, int):
                # if there's a single index, use parse to get the value it is stated to be
                # print(f"About to parse value {row[indices]} as type {self.Columns[indices]},\nFull list from row is {row},\nFull list of columns is {self.Columns},\nwith names {self.ColumnNames}")
                ret_val = TableSchema._parse(input=row[indices], col_schema=self.Columns[indices])
            elif isinstance(indices, list):
                ret_val = concatenator.join([str(row[index]) for index in indices])
            elif isinstance(indices, dict):
                ret_val = {}
                for key,column_index in indices.items():
                    if column_index > len(row):
                        Logger.Log(f"Got column index of {column_index} for column {key}, but row only has {len(row)} columns!", logging.ERROR)
                    _val = TableSchema._parse(input=row[column_index], col_schema=self._table_columns[column_index])
                    ret_val.update(_val if isinstance(_val, dict) else {key:_val})
        else:
            ret_val = fallback
        return ret_val
