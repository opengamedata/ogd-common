## import standard libraries
import abc
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, TypeAlias
## import local files
from ogd.common import schemas
from ogd.common.models.enums.TableType import TableType
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.utils import utils
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import conversions

ColumnMapIndex   : TypeAlias = Optional[int | List[int] | Dict[str,int]]
ColumnMapElement : TypeAlias = Optional[str | List[str] | Dict[str,str]]

## @class TableSchema
class TableSchema(Schema):
    """Dumb struct to hold info about the structure of data for a particular game, from a particular source.
        In particular, it contains an ordered list of columns in the data source table,
        and a mapping of those columns to the corresponding elements of a formal OGD structure.
    """

    @abc.abstractmethod
    @classmethod
    def _fromDict(cls, table_type:TableType, raw_map:Dict[str, ColumnMapElement], column_schemas:List[ColumnSchema]) -> "TableSchema":
        pass

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
        # declare and initialize vars
        # self._schema            : Optional[Dict[str, Any]] = all_elements
        self._table_type    : TableType                 = table_type
        self._column_map    : Dict[str, ColumnMapIndex] = column_map
        self._table_columns : List[ColumnSchema]        = columns

        # after loading the file, take the stuff we need and store.
        super().__init__(name=name, other_elements={})

    @property
    def Columns(self) -> List[ColumnSchema]:
        return self._table_columns

    @property
    def ColumnNames(self) -> List[str]:
        """Function to get the names of all columns in the schema.

        :return: Names of each column in the schema.
        :rtype: List[str]
        """
        return [col.Name for col in self._table_columns]

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        _column_map_markdown : str
        ret_val = "\n\n".join([
            "## Database Columns",
            "The individual columns recorded in the database for this game.",
            "\n".join([item.AsMarkdown for item in self.Columns]),
            f"## {self._table_type} Object Elements",
            "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.",
            self._columnMapMarkdown,
            ""])
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "TableSchema":
        _column_schemas : List[ColumnSchema]
        _table_type     : TableType

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} Table Schema, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _table_type_str   = all_elements.get('table_type')
        _table_type       = TableType.FromString(_table_type_str) if _table_type_str is not None else TableType.EVENT
        _column_json_list = all_elements.get('columns', [])
        _column_schemas   = [ColumnSchema.FromDict(name=column.get("name", "UNKNOWN COLUMN NAME"), all_elements=column) for column in _column_json_list]
        return cls._fromDict(table_type=_table_type, raw_map=all_elements.get('column_map', {}), column_schemas=_column_schemas)

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, schema_name:str, schema_path:Path = Path(schemas.__file__).parent / "table_schemas/") -> "TableSchema":
        _table_format_name : str = schema_name

        if not _table_format_name.lower().endswith(".json"):
            _table_format_name += ".json"
        _schema = utils.loadJSONFile(filename=_table_format_name, path=schema_path)

        return cls.FromDict(name=schema_name, all_elements=_schema)

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    @property
    def _columnMapMarkdown(self) -> str:
        ret_val : str

        event_column_list = []
        for event_element,columns_mapped in self._column_map.items():
            if columns_mapped is not None:
                if isinstance(columns_mapped, str):
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*'  ")
                elif isinstance(columns_mapped, list):
                    mapped_list = ", ".join([f"'*{item}*'" for item in columns_mapped])
                    event_column_list.append(f"**{event_element}** = Columns {mapped_list}  ") # figure out how to do one string foreach item in list.
                elif isinstance(columns_mapped, int):
                    event_column_list.append(f"**{event_element}** = Column '*{self.ColumnNames[columns_mapped]}*' (index {columns_mapped})  ")
                else:
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*' (DEBUG: Type {type(columns_mapped)})  ")
            else:
                event_column_list.append(f"**{event_element}** = null  ")
        ret_val = "\n".join(event_column_list)
        return ret_val

    def _getValueFromRow(self, row:Tuple, indices:Optional[int | List[int] | Dict[str, int]], concatenator:str, fallback:Any) -> Any:
        ret_val : Any
        if indices is not None:
            if isinstance(indices, int):
                # if there's a single index, use parse to get the value it is stated to be
                # print(f"About to parse value {row[indices]} as type {self.Columns[indices]},\nFull list from row is {row},\nFull list of columns is {self.Columns},\nwith names {self.ColumnNames}")
                ret_val = conversions.ConvertToType(variable=row[indices], to_type=self.Columns[indices].ValueType)
            elif isinstance(indices, list):
                ret_val = concatenator.join([str(row[index]) for index in indices])
            elif isinstance(indices, dict):
                ret_val = {}
                for key,column_index in indices.items():
                    if column_index > len(row):
                        Logger.Log(f"Got column index of {column_index} for column {key}, but row only has {len(row)} columns!", logging.ERROR)
                    _val = conversions.ConvertToType(variable=row[column_index], to_type=self._table_columns[column_index].ValueType)
                    ret_val.update(_val if isinstance(_val, dict) else {key:_val})
        else:
            ret_val = fallback
        return ret_val
