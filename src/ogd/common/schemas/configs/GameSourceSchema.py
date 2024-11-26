# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.storage.DataSourceSchema import DataSourceSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class GameSourceSchema(Schema):

    # *** BUILT-INS & PROPERTIES ***

    """A simple Schema structure containing configuration information for a particular game's data.

    TODO : use a TableSchema for the table_schema instead of just the name of the schema, like we do with source_schema.
    
    When given to an interface, this schema is treated as the location from which to retrieve data.
    When given to an outerface, this schema is treated as the location in which to store data.
    (note that some interfaces/outerfaces, such as debugging i/o-faces, may ignore the configuration)
    Key properties of this schema are:
    - `Name` : Typically, the name of the Game whose source configuration is indicated by this schema
    - `Source` : A data source where game data is stored
    - `DatabaseName` : The name of the specific database within the source that contains this game's data
    - `TableName` : The neame of the specific table within the database holding the given game's data
    - `TableSchema` : A schema indicating the structure of the table containing the given game's data.

    :param Schema: _description_
    :type Schema: _type_
    """
    def __init__(self, name:str,  game_id:Optional[str],
                 source_name:str, source_schema:Optional[DataSourceSchema],
                 db_name:str,     table_name:str,  table_schema:str,
                 other_elements:Dict[str, Any]):
        self._game_id       : str
        self._source_name   : str                        = source_name
        self._source_schema : Optional[DataSourceSchema] = source_schema
        self._db_name       : str                        = db_name
        self._table_name    : str                        = table_name
        self._table_schema  : str                        = table_schema

        super().__init__(name=name, other_elements=other_elements)
        if game_id is not None:
            self._game_id = game_id
        else:
            Logger.Log(f"GameSourceSchema did not receive a game_id, defaulting to {name}")
            self._game_id = name

    @property
    def GameID(self) -> str:
        return self._game_id

    @property
    def SourceName(self) -> str:
        return self._source_name

    @property
    def Source(self) -> Optional[DataSourceSchema]:
        return self._source_schema

    @property
    def DatabaseName(self) -> str:
        return self._db_name

    @property
    def TableName(self) -> str:
        return self._table_name

    @property
    def TableSchema(self) -> str:
        return self._table_schema

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: _{self.TableSchema}_ format, source {self.Source.Name if self.Source else 'None'} : {self.DatabaseName}.{self.TableName}"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger], data_sources:Dict[str, DataSourceSchema]) -> "GameSourceSchema":
        """Create a GameSourceSchema from a given dictionary

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataSourceSchema]
        :return: _description_
        :rtype: GameSourceSchema
        """
        _source_name   : str
        _source_schema : Optional[DataSourceSchema]
        _db_name       : str
        _table_schema  : str
        _table_name    : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} Game Source config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _source_name = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["source"],
            parser_function=cls._parseSource,
            default_value="UNKNOWN"
        )
        if _source_name in data_sources.keys():
            _source_schema = data_sources[_source_name]
        else:
            _source_schema = None
            _msg = f"{name} config's 'source' name ({_source_name}) was not found in available source schemas; defaulting to source_schema={_source_schema}"
            logger.warning(_msg) if logger else Logger.Log(_msg, logging.WARN)
        _db_name = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["database"],
            parser_function=cls._parseDBName,
            default_value=name
        )
        _table_name = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["table"],
            parser_function=cls._parseTableName,
            default_value="UNKNOWN"
        )
        _table_schema = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["schema"],
            parser_function=cls._parseTableSchemaName,
            default_value="UNKNOWN"
        )

        _used = {"source", "database", "table", "schema"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return GameSourceSchema(name=name, source_name=_source_name, source_schema=_source_schema,
                                db_name=_db_name, table_name=_table_name, table_schema=_table_schema,
                                other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    @staticmethod
    def EmptySchema() -> "GameSourceSchema":
        return GameSourceSchema(name="NOT FOUND", source_name="NOT FOUND", source_schema=None, db_name="NOT FOUND",
                                table_name="NOT FOUND", table_schema="NOT FOUND", other_elements={})

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseSource(source) -> str:
        ret_val : str
        if isinstance(source, str):
            ret_val = source
        else:
            ret_val = str(source)
            Logger.Log(f"Game Source source name was unexpected type {type(source)}, defaulting to str(source)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDBName(db_name) -> str:
        ret_val : str
        if isinstance(db_name, str):
            ret_val = db_name
        else:
            ret_val = str(db_name)
            Logger.Log(f"MySQL Data Source DB name was unexpected type {type(db_name)}, defaulting to str(db_name)={ret_val}.", logging.WARN)
        return ret_val

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
    def _parseTableSchemaName(table_schema_name) -> str:
        ret_val : str
        if isinstance(table_schema_name, str):
            ret_val = table_schema_name
        else:
            ret_val = str(table_schema_name)
            Logger.Log(f"Game Source table schema name type was unexpected type {type(table_schema_name)}, defaulting to str(schema)={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
