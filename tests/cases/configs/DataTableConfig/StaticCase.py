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
from src.ogd.common.configs.DataTableConfig import DataTableConfig
from tests.config.t_config import settings

class StaticCase(TestCase):
    """DataTableConfig test case to check that all loading and parsing work correctly.

    The test fixture here is technically "empty", since we don't define any data initially.
    We're ultimately just testing all the static functions here, and the name "static" is slightly more descriptive than "empty," hence StaticCase.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

    @staticmethod
    def RunAll():
        pass

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
        _schema = DataTableConfig.FromDict(name="AQUALAB", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "AQUALAB")
        self.assertIsInstance(_schema.StoreName, str)
        self.assertEqual(_schema.StoreName, "AQUALAB_BQ")
        self.assertIsInstance(_schema.DatabaseName, str)
        self.assertEqual(_schema.DatabaseName, "aqualab")
        self.assertIsInstance(_schema.TableName, str)
        self.assertEqual(_schema.TableName, "aqualab_daily")
        self.assertIsInstance(_schema.TableSchemaName, str)
        self.assertEqual(_schema.TableSchemaName, "OPENGAMEDATA_BIGQUERY")

    def test_parseSourceName(self):
        _map = {
            "source":"Foo",
            "fakekey" : "Bar"
        }
        _str = DataTableConfig._parseStoreName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")
        self.assertNotIn("source", _map) # First parse should remove key, so "source" should not exist anymore.
        
    def test_parseSourceName_missing(self):
        _map = {
            "fakekey" : "Bar"
        }
        _str = DataTableConfig._parseStoreName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, DataTableConfig._DEFAULT_STORE_NAME)

    def test_parseSourceName_alt_name(self):
        """Check that `source_name` is also treated as valid key for the source name.
        """
        _map = {
            "source_name":"Foo",
            "fakekey" : "Bar"
        }
        _str = DataTableConfig._parseStoreName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseSchemaName(self):
        _map = {
            "schema":"Foo",
            "fakekey" : "Bar"
        }
        _str = DataTableConfig._parseTableSchemaName(_map)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseTableLocation(self):
        _map = {
            "database":"Foo",
            "table":"Bar",
            "fakekey" : "Baz"
        }
        _loc = DataTableConfig._parseTableLocation(unparsed_elements=_map)
        self.assertIsInstance(_loc, DatabaseLocationSchema)
        self.assertIsInstance(_loc.DatabaseName, str)
        self.assertEqual(_loc.DatabaseName, "Foo")
        self.assertIsInstance(_loc.TableName, str)
        self.assertEqual(_loc.TableName, "Bar")


if __name__ == '__main__':
    unittest.main()
