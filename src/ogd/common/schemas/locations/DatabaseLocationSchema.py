## import standard libraries
from typing import Dict, List, Optional
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.typing import Map

## @class TableStructureSchema
class DatabaseLocationSchema(LocationSchema):
    """Class to encode the location of data within a database resource.

    Generally, the location of a database system would be a URLLocation,
    while DatabaseLocation refers to the location of a specific database or table within such a system.
    """

    _DEFAULT_DB_NAME = "DEFAULT_DB"
    _DEFAULT_TABLE_NAME = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, database_name:str, table_name:Optional[str], other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}

        self._db_name    : str           = database_name or self._parseDatabaseName(unparsed_elements=unparsed_elements)
        self._table_name : Optional[str] = table_name    or self._parseTableName(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def DatabaseName(self) -> str:
        """The name of the database, within a DB system, where the table is located.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._db_name

    @property
    def TableName(self) -> Optional[str]:
        return self._table_name

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return self.DatabaseName + ( f".{self._table_name}" if self.TableName else "" )

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.DatabaseName}.{self.TableName}"
        return ret_val

    @classmethod
    def Default(cls) -> "DatabaseLocationSchema":
        return DatabaseLocationSchema(
            name="DefaultDatabaseLocation",
            database_name=cls._DEFAULT_DB_NAME,
            table_name=cls._DEFAULT_TABLE_NAME,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "DatabaseLocationSchema":
        """Create a DatabaseLocationSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: GameSourceSchema
        """
        _table_name : Optional[str] = cls._parseTableName(unparsed_elements=unparsed_elements, key_overrides=key_overrides)
        _db_name    : str           = cls._parseDatabaseName(unparsed_elements=unparsed_elements, key_overrides=key_overrides)

        _used = {"table", "database"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return DatabaseLocationSchema(name=name, table_name=_table_name, database_name=_db_name, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseTableName(unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None) -> Optional[str]:
        default_keys : List[str] = ["table"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        return DatabaseLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=DatabaseLocationSchema._DEFAULT_TABLE_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseDatabaseName(unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None) -> str:
        default_keys : List[str] = ["database"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        return DatabaseLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=DatabaseLocationSchema._DEFAULT_DB_NAME,
            remove_target=True
        )
