## import standard libraries
import logging
from typing import Any, Dict, Optional
## import local files
from ogd.common.schemas.tables.locations.TableLocationSchema import TableLocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class TableStructureSchema
class DatabaseTableLocationSchema(TableLocationSchema):

    _DEFAULT_DB_NAME = "DEFAULT_DB"
    _DEFAULT_TABLE_NAME = "DEFAULT_TABLE"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, table_name:str, database_name:str, other_elements:Optional[Map]):
        unparsed_elements = other_elements or {}

        self._db_name = database_name or self._parseDatabaseName(unparsed_elements=unparsed_elements)
        super().__init__(name=name, table_name=table_name, other_elements=other_elements)

    @property
    def DatabaseName(self) -> str:
        """The name of the database, within a DB system, where the table is located.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._db_name

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.DatabaseName}.{self.TableName}"
        return ret_val

    @classmethod
    def Default(cls) -> "TableLocationSchema":
        return DatabaseTableLocationSchema(
            name="DefaultDatabaseTableLocation",
            table_name=cls._DEFAULT_TABLE_NAME,
            database_name=cls._DEFAULT_DB_NAME,
            other_elements={}
        )

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "DatabaseTableLocationSchema":
        """Create a TableLocationSchema from a given dictionary

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
        _table_name    : str

        if not isinstance(unparsed_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Table Location schema, unparsed_elements was not a dict, defaulting to empty dict", logging.WARN)
        _table_name = cls._parseTableName(unparsed_elements=unparsed_elements)
        _db_name = cls._parseDatabaseName(unparsed_elements=unparsed_elements)
        _used = {"table", "database"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return DatabaseTableLocationSchema(name=name, table_name=_table_name, database_name=_db_name, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseTableName(unparsed_elements:Map) -> str:
        return DatabaseTableLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["table"],
            to_type=str,
            default_value=DatabaseTableLocationSchema._DEFAULT_TABLE_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseDatabaseName(unparsed_elements:Map) -> str:
        return DatabaseTableLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["database"],
            to_type=str,
            default_value=DatabaseTableLocationSchema._DEFAULT_DB_NAME,
            remove_target=True
        )
