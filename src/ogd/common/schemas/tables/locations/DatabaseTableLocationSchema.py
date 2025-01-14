## import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, TypeAlias
## import local files
from ogd.common.schemas.tables.locations.TableLocationSchema import TableLocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

## @class TableStructureSchema
class DatabaseTableLocationSchema(TableLocationSchema):

    _DEFAULT_DB_NAME = "DEFAULT_DB"
    _DEFAULT_TABLE_NAME = "DEFAULT_TABLE"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, table_name:str, database_name:str, other_elements:Optional[Map]):
        self._db_name = database_name
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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]) -> "DatabaseTableLocationSchema":
        """Create a TableLocationSchema from a given dictionary

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

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} Table Location schema, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _table_name = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["table"],
            parser_function=cls._parseTableName,
            default_value=DatabaseTableLocationSchema._DEFAULT_TABLE_NAME
        )
        _db_name = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["database"],
            parser_function=cls._parseDatabaseName,
            default_value=DatabaseTableLocationSchema._DEFAULT_DB_NAME
        )

        _used = {"table", "database"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return DatabaseTableLocationSchema(name=name, table_name=_table_name, database_name=_db_name, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseTableName(table) -> str:
        ret_val : str
        if isinstance(table, str):
            ret_val = table
        else:
            ret_val = str(table)
            Logger.Log(f"Game Source table name was unexpected type {type(table)}, defaulting to str(table)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDatabaseName(table) -> str:
        ret_val : str
        if isinstance(table, str):
            ret_val = table
        else:
            ret_val = str(table)
            Logger.Log(f"Game Source table name was unexpected type {type(table)}, defaulting to str(table)={ret_val}.", logging.WARN)
        return ret_val
