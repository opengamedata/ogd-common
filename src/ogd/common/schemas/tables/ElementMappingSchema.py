# import standard libraries
import logging
from typing import Any, Dict, List, Optional, TypeAlias
# import local files
from ogd.common.models.enums.ElementMappingType import ElementMappingType
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

ElementMap: TypeAlias = ColumnSchema | List[ColumnSchema] | Dict[str,ColumnSchema]

class ElementMappingSchema(Schema):
    """Simple struct-like class to define a mapping of one or more data table columns to a single GameData element.

    For example, the following JSON-style mapping definition for the EventData element of an Event:
    ```json
    "event_data" : { "item1":"someColumn", "item2":"someOtherColumn" }
    ```
    would result in an ElementMappingSchema with name "EventData", mapping type "DICT" and mapping definition like:
    ```python
    {
        "item1" : <ColumnSchema for "someColumn">,
        "item2" : <ColumnSchema for "someOtherColumn">
    }
    ```
    """

    _DEFAULT_MAP = {}
    _DEFAULT_COLUMN_NAMES = []

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, map:ElementMap, other_elements:Optional[Map]=None):
        self._map      : ElementMap = map
        self._map_type : ElementMappingType
        if isinstance(map, ColumnSchema):
            self._map_type = ElementMappingType.SINGLE
        elif isinstance(map, list):
            self._map_type = ElementMappingType.LIST
        elif isinstance(map, dict):
            self._map_type = ElementMappingType.DICT
        else:
            raise TypeError(f"The map passed to ElementMappingSchema had invalide type {type(map)}")
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Map(self) -> ElementMap:
        return self._map

    @property
    def ColumnNames(self) -> List[str]:
        match self._map_type:
            case ElementMappingType.SINGLE:
                

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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], column_names:List[str], logger:Optional[logging.Logger]=None)-> "ElementMappingSchema":
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
        _map : Dict[str, ElementMappingSchema.ElementMapIndex] = {
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

        return ElementMappingSchema(name=name, map=_map, column_names=column_names, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "ElementMappingSchema":
        return ElementMappingSchema(
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
