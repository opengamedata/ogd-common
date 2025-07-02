# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class GameSourceSchema(Schema):
    """A simple Schema structure containing configuration information for a particular game's data.
    
    When given to an interface, this schema is treated as the location from which to retrieve data.
    When given to an outerface, this schema is treated as the location in which to store data.
    (note that some interfaces/outerfaces, such as debugging i/o-faces, may ignore the configuration)
    Key properties of this schema are:
    - `Name` : Typically, the name of the Game whose source configuration is indicated by this schema
    - `Source` : A data source where game data is stored
    - `DatabaseName` : The name of the specific database within the source that contains this game's data
    - `TableName` : The neame of the specific table within the database holding the given game's data
    - `TableSchema` : A schema indicating the structure of the table containing the given game's data.

    TODO : use a TableSchema for the table_schema instead of just the name of the schema, like we do with source_schema.
    TODO : Implement and use a smart Load(...) function of TableSchema to load schema from given name, rather than FromFile.
    """

    _DEFAULT_GAME_ID       = "UNKNOWN GAME"
    _DEFAULT_SOURCE_NAME   = "OPENGAMEDATA_BQ"
    _DEFAULT_DB_NAME       = "UNKNOWN GAME"
    _DEFAULT_TABLE_NAME    = "_daily"
    _DEFAULT_TABLE_SCHEMA  = "OPENGAMEDATA_BIGQUERY"
    _DEFAULT_TABLE_FOLDER_PATH = Path("./tables/")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,  game_id:Optional[str],
                 source_name:str, source_schema:Optional[DataStoreConfig],
                 db_name:str,     table_name:str,  table_schema:str,
                 other_elements:Optional[Map]):
        unparsed_elements : Map = other_elements or {}

        self._game_id           : str                       = game_id       or self._parseGameID(unparsed_elements=unparsed_elements, name=name)
        self._source_name       : str                       = source_name   or self._parseSourceName(unparsed_elements=unparsed_elements)
        self._source_schema     : Optional[DataStoreConfig] = source_schema
        self._db_name           : str                       = db_name       or self._parseDBName(unparsed_elements=unparsed_elements)
        self._table_name        : str                       = table_name    or self._parseTableName(unparsed_elements=unparsed_elements)
        self._table_schema_name : str                       = table_schema  or self._parseTableSchemaName(unparsed_elements=unparsed_elements)
        self._table_schema      : TableSchema = TableSchema.FromFile(schema_name=self._table_schema_name, schema_path=self._DEFAULT_TABLE_FOLDER_PATH)

        if game_id is not None:
            self._game_id = game_id
        else:
            Logger.Log(f"GameSourceSchema did not receive a game_id, defaulting to {name}")
            self._game_id = name
        super().__init__(name=name, other_elements=other_elements)

    @property
    def GameID(self) -> str:
        """Property to get the Game ID (also called App ID) associated with the given game source

        By convention, this is a human-readable simplification of the games name, in CONSTANT_CASE format

        :return: _description_
        :rtype: str
        """
        return self._game_id

    @property
    def SourceName(self) -> str:
        return self._source_name

    @property
    def Source(self) -> Optional[DataStoreConfig]:
        return self._source_schema

    @property
    def DatabaseName(self) -> str:
        return self._db_name

    @property
    def TableName(self) -> str:
        return self._table_name

    @property
    def TableSchema(self) -> TableSchema:
        return self._table_schema

    @property
    def TableSchemaName(self) -> str:
        return self._table_schema_name

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: _{self.TableSchemaName}_ format, source {self.Source.Name if self.Source else 'None'} : {self.DatabaseName}.{self.TableName}"
        return ret_val

    @classmethod
    def Default(cls) -> "GameSourceSchema":
        return GameSourceSchema(
            name="DefaultGameSourceSchema",
            game_id=cls._DEFAULT_GAME_ID,
            source_name=cls._DEFAULT_SOURCE_NAME,
            source_schema=BigQueryConfig.Default(),
            db_name=cls._DEFAULT_DB_NAME,
            table_name=cls._DEFAULT_TABLE_NAME,
            table_schema=cls._DEFAULT_TABLE_SCHEMA,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any], data_sources:Dict[str, DataStoreConfig]) -> "GameSourceSchema":
        """Create a GameSourceSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.
        TODO : data_sources shouldn't really be a param here. Better to have e.g. a way to register the list into GameSourceSchema class, or something.

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
        _game_id       : str                       = cls._parseGameID(unparsed_elements=unparsed_elements)
        _db_name       : str                       = cls._parseDBName(unparsed_elements=unparsed_elements)
        _table_schema  : str                       = cls._parseTableSchemaName(unparsed_elements=unparsed_elements)
        _table_name    : str                       = cls._parseTableName(unparsed_elements=unparsed_elements)

        _source_name   : str                       = cls._parseSourceName(unparsed_elements=unparsed_elements)
        _source_schema : Optional[DataStoreConfig] = None

        if _source_name in data_sources.keys():
            _source_schema = data_sources[_source_name]
        else:
            _msg = f"{name} config's 'source' name ({_source_name}) was not found in available source schemas; defaulting to source_schema={_source_schema}"
            Logger.Log(_msg, logging.WARN)

        _used = {"source", "source_name", "database", "table", "schema"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return GameSourceSchema(name=name, game_id=_game_id, source_name=_source_name, source_schema=_source_schema,
                                db_name=_db_name, table_name=_table_name, table_schema=_table_schema,
                                other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any], data_sources:Dict[str, DataStoreConfig]) -> "GameSourceSchema":
        if not isinstance(unparsed_elements, dict):
            unparsed_elements   = {}
            _msg = f"For {name} {cls.__name__}, unparsed_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)

        return cls._fromDict(name=name, unparsed_elements=unparsed_elements, data_sources=data_sources)

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseSourceName(unparsed_elements:Map) -> str:
        return GameSourceSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["source", "source_name"],
            to_type=str,
            default_value=GameSourceSchema._DEFAULT_SOURCE_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseGameID(unparsed_elements:Map, name:Optional[str]=None) -> str:
        return GameSourceSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game", "game_id"],
            to_type=str,
            default_value=name or GameSourceSchema._DEFAULT_GAME_ID,
            remove_target=True
        )

    @staticmethod
    def _parseDBName(unparsed_elements:Map) -> str:
        return GameSourceSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["database"],
            to_type=str,
            default_value=GameSourceSchema._DEFAULT_DB_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseTableName(unparsed_elements:Map) -> str:
        return GameSourceSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["table"],
            to_type=str,
            default_value=GameSourceSchema._DEFAULT_TABLE_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseTableSchemaName(unparsed_elements:Map) -> str:
        return GameSourceSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["schema"],
            to_type=str,
            default_value=GameSourceSchema._DEFAULT_TABLE_SCHEMA,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
