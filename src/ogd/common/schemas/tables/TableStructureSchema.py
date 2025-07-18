## import standard libraries
import abc
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, TypeAlias
## import local files
from ogd.common import schemas
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

ColumnMapIndex   : TypeAlias = Optional[int | List[int] | Dict[str,int]]
ColumnMapElement : TypeAlias = Optional[str | List[str] | Dict[str,str]]

## @class TableStructureSchema
class TableStructureSchema(Schema):
    """Dumb struct to hold info about the structure of data for a particular game, from a particular source.
        In particular, it contains an ordered list of columns in the data source table,
        and a mapping of those columns to the corresponding elements of a formal OGD structure.
    """

    @classmethod
    @abc.abstractmethod
    def _subparseDict(cls, name:str, raw_map:Dict[str, ColumnMapElement], column_schemas:List[ColumnSchema], logger:Optional[logging.Logger]=None) -> "TableStructureSchema":
        pass

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_COLUMNS = []

    def __init__(self, name, column_map:Dict[str, ColumnMapIndex], columns:List[ColumnSchema], other_elements:Optional[Map]=None):
        """Constructor for the TableStructureSchema class.
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
        self._column_map    : Dict[str, ColumnMapIndex] = column_map
        self._table_columns : List[ColumnSchema]        = columns

        # after loading the file, take the stuff we need and store.
        super().__init__(name=name, other_elements=other_elements)

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

    @property
    def ColumnMap(self) -> Dict[str, ColumnMapIndex]:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indicies, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._column_map

    @property
    def AppIDIndex(self) -> ColumnMapIndex:
        return self._column_map['app_id']

    @property
    def AppIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.AppIDIndex, int):
            ret_val = self.ColumnNames[self.AppIDIndex]
        elif isinstance(self.AppIDIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.AppIDIndex])
        return ret_val

    @property
    def UserIDIndex(self) -> ColumnMapIndex:
        return self._column_map['user_id']

    @property
    def UserIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.UserIDIndex, int):
            ret_val = self.ColumnNames[self.UserIDIndex]
        elif isinstance(self.UserIDIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.UserIDIndex])
        return ret_val

    @property
    def SessionIDIndex(self) -> ColumnMapIndex:
        return self._column_map['session_id']

    @property
    def SessionIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.SessionIDIndex, int):
            ret_val = self.ColumnNames[self.SessionIDIndex]
        elif isinstance(self.SessionIDIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.SessionIDIndex])
        return ret_val

    @property
    def AppVersionIndex(self) -> ColumnMapIndex:
        return self._column_map['app_version']

    @property
    def AppVersionColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.AppVersionIndex, int):
            ret_val = self.ColumnNames[self.AppVersionIndex]
        elif isinstance(self.AppVersionIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.AppVersionIndex])
        return ret_val

    @property
    def AppBranchIndex(self) -> ColumnMapIndex:
        return self._column_map['app_branch']

    @property
    def AppBranchColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.AppBranchIndex, int):
            ret_val = self.ColumnNames[self.AppBranchIndex]
        elif isinstance(self.AppBranchIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.AppBranchIndex])
        return ret_val

    @property
    def LogVersionIndex(self) -> ColumnMapIndex:
        return self._column_map['log_version']

    @property
    def LogVersionColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self.LogVersionIndex, int):
            ret_val = self.ColumnNames[self.LogVersionIndex]
        elif isinstance(self.LogVersionIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self.LogVersionIndex])
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "TableStructureSchema":
        """Function to generate a TableStructureSchema from a dictionary.

        The structure is assumed to be as follows:
        ```python
        {
            "table_type" : <either EVENT or FEATURE>,
            "columns" : [<list of column schemas>],
            "column_map" : {<mapping of column names to indices>}
        }
        ```

        The specific handling of the column map will be determined by the specific TableStructureSchema subclass on which the FromDict feature is called.

        :param name: The name of the returned TableStructureSchema object
        :type name: str
        :param all_elements: A dictionary containing all elements to be parsed into the TableStructureSchema object
        :type all_elements: Dict[str, Any]
        :param logger: An optional logger for outputting errors/warnings, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: An instance of the TableStructureSchema subclass on which the function is called
        :rtype: TableStructureSchema
        """
        _column_json_list : List               = unparsed_elements.get('columns', [])
        _column_schemas   : List[ColumnSchema] = [ColumnSchema.FromDict(name=column.get("name", "UNKNOWN COLUMN NAME"), unparsed_elements=column) for column in _column_json_list]
        return cls._subparseDict(name=name, raw_map=unparsed_elements.get('column_map', {}), column_schemas=_column_schemas)

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, schema_name:str, schema_path:Optional[str | Path], search_templates:bool=False) -> "TableStructureSchema":
        ret_val : Schema

        schema_path = schema_path or Path(schemas.__file__).parent / "table_schemas"
        ret_val = cls._fromFile(schema_name=schema_name, schema_path=Path(schema_path))
        if isinstance(ret_val, TableStructureSchema):
            return ret_val
        else:
            raise ValueError("TableStructureSchema's call to _fromFile yielded a Schema of different type!")

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    @property
    def _columnSetMarkdown(self) -> str:
        return "\n".join([item.AsMarkdown for item in self.Columns])

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
    
    @staticmethod
    def _retrieveElement(elem:Any, name:str) -> Optional[ColumnMapElement]:
        """_summary_

        :param elem: _description_
        :type elem: Any
        :param name: _description_
        :type name: str
        :return: _description_
        :rtype: Optional[ColumnMapElement]
        """
        ret_val : Optional[str | List[str] | Dict[str, str]]
        if elem is not None:
            if isinstance(elem, str):
                ret_val = elem
            elif isinstance(elem, list):
                ret_val = elem
            elif isinstance(elem, dict):
                ret_val = elem
            else:
                ret_val = str(elem)
                Logger.Log(f"Column name(s) mapped to {name} was not a string or list, defaulting to str(name) == {ret_val} being mapped to {name}", logging.WARN)
        else:
            ret_val = None
            Logger.Log(f"Column name mapped to {name} was left null, nothing will be mapped to {name}", logging.WARN)
        return ret_val

    def _getValueFromRow(self, row:Tuple, indices:Optional[int | List[int] | Dict[str, int]], concatenator:str, fallback:Any) -> Any:
        ret_val : Any
        if indices is not None:
            if isinstance(indices, int):
                # if there's a single index, use parse to get the value it is stated to be
                # print(f"About to parse value {row[indices]} as type {self.Columns[indices]},\nFull list from row is {row},\nFull list of columns is {self.Columns},\nwith names {self.ColumnNames}")
                ret_val = conversions.ConvertToType(value=row[indices], to_type=self.Columns[indices].ValueType)
            elif isinstance(indices, list):
                ret_val = concatenator.join([str(row[index]) for index in indices])
            elif isinstance(indices, dict):
                ret_val = {}
                for key,column_index in indices.items():
                    if column_index > len(row):
                        Logger.Log(f"Got column index of {column_index} for column {key}, but row only has {len(row)} columns!", logging.ERROR)
                    _val = conversions.ConvertToType(value=row[column_index], to_type=self._table_columns[column_index].ValueType)
                    ret_val.update(_val if isinstance(_val, dict) else {key:_val})
        else:
            ret_val = fallback
        return ret_val
