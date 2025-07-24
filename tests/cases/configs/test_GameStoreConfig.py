# import libraries
import logging
import unittest
from typing import Dict
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.schemas.locations.DatabaseLocationSchema import DatabaseLocationSchema
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.configs.GameStoreConfig import GameStoreConfig
from tests.config.t_config import settings

class test_GameStoreConfig(TestCase):
    """Testbed for the GameStoreConfig class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        source_elems = {
            "DB_TYPE"    : "BIGQUERY",
            "PROJECT_ID" : "aqualab-project",
            "PROJECT_KEY": {
                "FILE": "key.txt",
                "PATH": "./"
            }
        }
        cls.test_schema = GameStoreConfig(
            name="Game Source Schema",
            game_id="AQUALAB",
            source_name="AQUALAB_BQ",
            schema_name=BigQueryConfig.FromDict(name="AQUALAB_BQ", unparsed_elements=source_elems),
            table_location=DatabaseLocationSchema(name="DBLocation", database_name="aqualab", table_name="aqualab_daily"),
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

    def test_SchemaName(self):
        """Test the correctness of TableConfig property
        """
        _str = self.test_schema.SchemaName
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
        _schema = GameStoreConfig.FromDict(name="AQUALAB", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "AQUALAB")
        self.assertIsInstance(_schema.SourceName, str)
        self.assertEqual(_schema.SourceName, "AQUALAB_BQ")
        self.assertIsInstance(_schema.DatabaseName, str)
        self.assertEqual(_schema.DatabaseName, "aqualab")
        self.assertIsInstance(_schema.TableName, str)
        self.assertEqual(_schema.TableName, "aqualab_daily")
        self.assertIsInstance(_schema.SchemaName, str)
        self.assertEqual(_schema.SchemaName, "OPENGAMEDATA_BIGQUERY")

    def test_parseSourceName(self):
        _map = {
            "source":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameStoreConfig._parseSourceName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")
        # First parse should remove key, so second should return default from class
        _str = GameStoreConfig._parseSourceName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, GameStoreConfig._DEFAULT_SOURCE_NAME)
        # Check that source_name is also treated as valid
        _map = {
            "source_name":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameStoreConfig._parseSourceName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseSchemaName(self):
        _map = {
            "schema":"Foo",
            "fakekey" : "Bar"
        }
        _str = GameStoreConfig._parseSchemaName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseTableLocation(self):
        _map = {
            "database":"Foo",
            "table":"Bar",
            "fakekey" : "Baz"
        }
        _loc = GameStoreConfig._parseTableLocation(unparsed_elements=_map)
        self.assertIsInstance(_loc, DatabaseLocationSchema)
        self.assertIsInstance(_loc.DatabaseName, str)
        self.assertEqual(_loc.DatabaseName, "Foo")
        self.assertIsInstance(_loc.TableName, str)
        self.assertEqual(_loc.TableName, "Bar")


if __name__ == '__main__':
    unittest.main()
