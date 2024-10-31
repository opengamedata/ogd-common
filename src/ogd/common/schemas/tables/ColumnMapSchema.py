# import standard libraries
import logging
from typing import Any, Dict, List, Optional, TypeAlias
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.utils.Logger import Logger

class ColumnMapSchema(Schema):
    ColumnMapIndex : TypeAlias = Optional[int | List[int] | Dict[str,int]]

    _DEFAULT_MAP = {}
    _DEFAULT_COLUMN_NAMES = []

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, map:Dict[str, ColumnMapIndex], column_names:List[str], other_elements:Dict[str, Any]={}):
        self._map            : Dict[str, ColumnMapSchema.ColumnMapIndex] = map
        self._column_names   : List[str]                                   = column_names

        super().__init__(name=name, other_elements=other_elements)

    @property
    def Map(self) -> Dict[str, ColumnMapIndex]:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indicies, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._map

    @property
    def SessionID(self) -> ColumnMapIndex:
        return self._map['session_id']

    @property
    def AppID(self) -> ColumnMapIndex:
        return self._map['app_id']

    @property
    def Timestamp(self) -> ColumnMapIndex:
        return self._map['timestamp']

    @property
    def EventName(self) -> ColumnMapIndex:
        return self._map['event_name']

    @property
    def EventData(self) -> ColumnMapIndex:
        return self._map['event_data']

    @property
    def EventSource(self) -> ColumnMapIndex:
        return self._map['event_source']

    @property
    def AppVersion(self) -> ColumnMapIndex:
        return self._map['app_version']

    @property
    def AppBranch(self) -> ColumnMapIndex:
        return self._map['app_branch']

    @property
    def LogVersion(self) -> ColumnMapIndex:
        return self._map['log_version']

    @property
    def TimeOffset(self) -> ColumnMapIndex:
        return self._map['time_offset']

    @property
    def UserID(self) -> ColumnMapIndex:
        return self._map['user_id']

    @property
    def UserData(self) -> ColumnMapIndex:
        return self._map['user_data']

    @property
    def GameState(self) -> ColumnMapIndex:
        return self._map['game_state']

    @property
    def EventSequenceIndex(self) -> ColumnMapIndex:
        return self._map['event_sequence_index']

    @property
    def Elements(self) -> Dict[str, str]:
        return self._other_elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._other_elements.keys())

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        event_column_list = []
        for evt_col,row_col in self._map.items():
            if row_col is not None:
                if isinstance(row_col, str):
                    event_column_list.append(f"**{evt_col}** = Column '*{row_col}*'  ")
                elif isinstance(row_col, list):
                    mapped_list = ", ".join([f"'*{item}*'" for item in row_col])
                    event_column_list.append(f"**{evt_col}** = Columns {mapped_list}  ") # figure out how to do one string foreach item in list.
                elif isinstance(row_col, int):
                    event_column_list.append(f"**{evt_col}** = Column '*{self._column_names[row_col]}*' (index {row_col})  ")
                else:
                    event_column_list.append(f"**{evt_col}** = Column '*{row_col}*' (DEBUG: Type {type(row_col)})  ")
            else:
                event_column_list.append(f"**{evt_col}** = null  ")
        ret_val = "\n".join(event_column_list)
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], column_names:List[str], logger:Optional[logging.Logger]=None)-> "ColumnMapSchema":
        """Function to generate a ColumnMapSchema from a JSON object

        TODO : find a way around using column_names as a direct parameter.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param column_names: _description_
        :type column_names: List[str]
        :param logger: _description_, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: _description_
        :rtype: ColumnMapSchema
        """
        _map : Dict[str, ColumnMapSchema.ColumnMapIndex] = {
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

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} column map schema, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        # for each item in the map above that we expect...
        for key in _map.keys():
            # if the item was found in the given "column_map" dictionary...
            if key in all_elements:
                # parse what was mapped to the item. Could get back a string, or a list, or a dict...
                element = cls._parseElement(elem=map[key], name=key)
                # then if we got a string, we just find it in list of column names
                if isinstance(element, str):
                    _map[key] = column_names.index(element)
                # but if it's a list, we need to get index of each item in list of column names
                elif isinstance(element, list):
                    _map[key] = [column_names.index(listelem) for listelem in element]
                # but if it's a dict, we need to make equivalent dict mapping the key (new name) to the index (in list of column names)
                elif isinstance(element, dict):
                    _map[key] = {key : column_names.index(listelem) for key,listelem in element.items()}
            else:
                Logger.Log(f"Column config does not have a '{key}' element, defaulting to {key} : None", logging.WARN)
        _leftovers = { key : val for key,val in all_elements.items() if key not in _map.keys() }

        return ColumnMapSchema(name=name, map=_map, column_names=column_names, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "ColumnMapSchema":
        return ColumnMapSchema(
            name="DefaultColumnMapSchema",
            map=cls._DEFAULT_MAP,
            column_names=cls._DEFAULT_COLUMN_NAMES,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseElement(elem:Any, name:str) -> Optional[str | List[str] | Dict[str, str]]:
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

    # *** PRIVATE METHODS ***
