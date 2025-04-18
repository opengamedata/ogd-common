# import libraries
import logging
import unittest
from typing import Dict
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.configs.GameSourceSchema import GameSourceSchema
from tests.config.t_config import settings

class t_GameSourceSchema(TestCase):
    """Testbed for the GameSourceSchema class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        source_elems = {
            "DB_TYPE"    : "FIREBASE",
            "PROJECT_ID" : "aqualab-project",
            "PROJECT_KEY": "./key.txt"
        }
        cls.test_schema = GameSourceSchema(
            name="Game Source Schema",
            game_id="AQUALAB",
            source_name="AQUALAB_BQ",
            source_schema=BigQueryConfig.FromDict(name="AQUALAB_BQ", unparsed_elements=source_elems),
            db_name="aqualab",
            table_name="aqualab_daily",
            table_schema="OPENGAMEDATA_BIGQUERY",
            other_elements={ "foo":"bar" }
        )

    @staticmethod
    def RunAll():
        pass

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Game Source Schema")

    def test_SourceName(self):
        _str = self.test_schema.SourceName
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "AQUALAB_BQ")

    @unittest.skip("Not yet implemented")
    def test_Source(self):
        pass
        # _str = self.test_schema.SourceName
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "AQUALAB_BQ")

    def test_DatabaseName(self):
        _str = self.test_schema.DatabaseName
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "aqualab")

    def test_TableName(self):
        _str = self.test_schema.TableName
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "aqualab_daily")

    def test_TableSchema(self):
        """Test the correctness of TableSchema property
        """
        _str = self.test_schema.TableSchemaName
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "OPENGAMEDATA_BIGQUERY")

    def test_NonStandardElements(self):
        _elems = {
            "foo":"bar"
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    def test_NonStandardElementNames(self):
        _elem_names = ["foo"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)

    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.

            TODO : Include assertion(s) for DataStoreConfig, as in implementation of test_Source (whenever that gets implemented)
            TODO : Possibly do additional cases where we check that default replacements for missing elements are correct.
        """
        _dict = {
            "source":"AQUALAB_BQ",
            "database":"aqualab",
            "table":"aqualab_daily",
            "schema":"OPENGAMEDATA_BIGQUERY"
        }
        source_elems = {
            "DB_TYPE"    : "FIREBASE",
            "PROJECT_ID" : "aqualab-project",
            "PROJECT_KEY": "./key.txt"
        }
        _sources : Dict[str, DataStoreConfig] = { "AQUALAB_BQ" : BigQueryConfig.FromDict(name="AQUALAB_BQ", unparsed_elements=source_elems) }
        _schema = GameSourceSchema.FromDict(name="AQUALAB", unparsed_elements=_dict, data_sources=_sources)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "AQUALAB")
        self.assertIsInstance(_schema.SourceName, str)
        self.assertEqual(_schema.SourceName, "AQUALAB_BQ")
        self.assertIsInstance(_schema.Source, DataStoreConfig)
        # self.assertEqual(_schema.Source, "AQUALAB")
        self.assertIsInstance(_schema.DatabaseName, str)
        self.assertEqual(_schema.DatabaseName, "aqualab")
        self.assertIsInstance(_schema.TableName, str)
        self.assertEqual(_schema.TableName, "aqualab_daily")
        self.assertIsInstance(_schema.TableSchemaName, str)
        self.assertEqual(_schema.TableSchemaName, "OPENGAMEDATA_BIGQUERY")

    def test_parseSource(self):
        _map = {
            "source":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameSourceSchema._parseSourceName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")
        # First parse should remove key, so second should return default from class
        _str = GameSourceSchema._parseSourceName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, GameSourceSchema._DEFAULT_SOURCE_NAME)
        # Check that source_name is also treated as valid
        _map = {
            "source_name":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameSourceSchema._parseSourceName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseGameID(self):
        _map = {
            "game":"Foo",
            "fakekey" : "Bar",
            "game_id" : "Baz"
        }
        _str = GameSourceSchema._parseGameID(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")
        # first parse should remove "game" key, so second attempt should give "Baz"
        _str = GameSourceSchema._parseGameID(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Baz")

    def test_parseDBName(self):
        _map = {
            "database":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameSourceSchema._parseDBName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseTableName(self):
        _map = {
            "table":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameSourceSchema._parseTableName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseTableSchemaName(self):
        _map = {
            "schema":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameSourceSchema._parseTableSchemaName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")


if __name__ == '__main__':
    unittest.main()
