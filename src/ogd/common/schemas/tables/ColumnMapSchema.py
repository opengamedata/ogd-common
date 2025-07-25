## import standard libraries
import abc
import logging
from typing import Dict, List, Optional, Self, TypeAlias
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.utils.typing import Map

ColumnMapIndex   : TypeAlias = Optional[int | List[int] | Dict[str,int]]
ColumnMapElement : TypeAlias = Optional[str | List[str] | Dict[str,str]]

## @class TableSchema
class ColumnMapSchema(Schema):

    @classmethod
    @abc.abstractmethod
    def _subparseDict(cls, name:str, raw_map:Dict[str, ColumnMapElement], column_schemas:List[ColumnSchema], logger:Optional[logging.Logger]=None) -> Self:
        pass

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_COLUMNS = []

    def __init__(self, name,
                 app_id:Optional[ColumnMapElement],    user_id:Optional[ColumnMapElement],     session_id:Optional[ColumnMapElement],
                 app_version:Optional[ColumnMapElement], app_branch:Optional[ColumnMapElement], log_version:Optional[ColumnMapElement],
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the TableSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
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

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        # declare and initialize vars
        self._raw_map : Map = other_elements or {}

        self._app_id      : ColumnMapElement = app_id      or self._parseAppID(unparsed_elements=self._raw_map)
        self._user_id     : ColumnMapElement = user_id     or self._parseUserID(unparsed_elements=self._raw_map)
        self._session_id  : ColumnMapElement = session_id  or self._parseSessionID(unparsed_elements=self._raw_map)
        self._app_version : ColumnMapElement = app_version or self._parseAppVersion(unparsed_elements=self._raw_map)
        self._app_branch  : ColumnMapElement = app_branch  or self._parseAppBranch(unparsed_elements=self._raw_map)
        self._log_version : ColumnMapElement = log_version or self._parseLogVersion(unparsed_elements=self._raw_map)

        # after loading the file, take the stuff we need and store.
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Mapping(self) -> Dict[str, ColumnMapElement]:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indicies, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._raw_map

    @property
    def AppIDColumn(self) -> ColumnMapElement:
        return self._app_id

    @property
    def UserIDColumn(self) -> ColumnMapElement:
        return self._user_id

    @property
    def SessionIDColumn(self) -> ColumnMapElement:
        return self._session_id

    @property
    def AppVersionColumn(self) -> ColumnMapElement:
        return self._app_version

    @property
    def AppBranchColumn(self) -> ColumnMapElement:
        return self._app_branch

    @property
    def LogVersionColumn(self) -> ColumnMapElement:
        return self._log_version

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        event_column_list = []
        for event_element,columns_mapped in self.Mapping.items():
            if columns_mapped is not None:
                if isinstance(columns_mapped, str):
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*'  ")
                elif isinstance(columns_mapped, int):
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*'  ")
                elif isinstance(columns_mapped, list):
                    mapped_list = ", ".join([f"'*{item}*'" for item in columns_mapped])
                    event_column_list.append(f"**{event_element}** = Columns {mapped_list}  ") # figure out how to do one string foreach item in list.
                else:
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*' (DEBUG: Type {type(columns_mapped)})  ")
            else:
                event_column_list.append(f"**{event_element}** = null  ")
        ret_val = "\n".join(event_column_list)
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    # @staticmethod
    # def _retrieveElement(elem:Any, name:str) -> Optional[ColumnMapElement]:
    #     """_summary_

    #     :param elem: _description_
    #     :type elem: Any
    #     :param name: _description_
    #     :type name: str
    #     :return: _description_
    #     :rtype: Optional[ColumnMapElement]
    #     """
    #     ret_val : Optional[str | List[str] | Dict[str, str]]
    #     if elem is not None:
    #         if isinstance(elem, str):
    #             ret_val = elem
    #         elif isinstance(elem, list):
    #             ret_val = elem
    #         elif isinstance(elem, dict):
    #             ret_val = elem
    #         else:
    #             ret_val = str(elem)
    #             Logger.Log(f"Column name(s) mapped to {name} was not a string or list, defaulting to str(name) == {ret_val} being mapped to {name}", logging.WARN)
    #     else:
    #         ret_val = None
    #         Logger.Log(f"Column name mapped to {name} was left null, nothing will be mapped to {name}", logging.WARN)
    #     return ret_val

    @staticmethod
    def _parseAppID(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["app_id", "game_id"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseUserID(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["user_id", "player_id"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseSessionID(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["session_id"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )
    @staticmethod
    def _parseAppVersion(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["app_version"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseAppBranch(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["app_branch", "app_flavor"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseLogVersion(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["log_version"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    # *** PRIVATE METHODS ***
