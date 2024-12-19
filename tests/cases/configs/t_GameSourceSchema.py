# import libraries
import datetime
import logging
import unittest
from typing import Any, Dict, Optional
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.configs.GameSourceSchema import GameSourceSchema
from tests.config.t_config import settings

class t_GameSourceSchema(TestCase):
    """Testbed for the GameSourceSchema class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", all_elements=settings, logger=None)
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
            source_schema=BigQueryConfig.FromDict(name="AQUALAB_BQ", all_elements=source_elems, logger=None),
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
        _sources : Dict[str, DataStoreConfig] = { "AQUALAB_BQ" : BigQueryConfig.FromDict(name="AQUALAB_BQ", all_elements=source_elems, logger=None) }
        _schema = GameSourceSchema.FromDict(name="AQUALAB", all_elements=_dict, logger=None, data_sources=_sources)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "AQUALAB")
        self.assertIsInstance(_schema.SourceName, str)
        self.assertEqual(_schema.SourceName, "AQUALAB_BQ")
        # self.assertIsInstance(_schema.Source, DataStoreConfig)
        # self.assertEqual(_schema.Source, "AQUALAB")
        self.assertIsInstance(_schema.DatabaseName, str)
        self.assertEqual(_schema.DatabaseName, "aqualab")
        self.assertIsInstance(_schema.TableName, str)
        self.assertEqual(_schema.TableName, "aqualab_daily")
        self.assertIsInstance(_schema.TableSchemaName, str)
        self.assertEqual(_schema.TableSchemaName, "OPENGAMEDATA_BIGQUERY")

    @unittest.skip("Not yet implemented")
    def test_parseSource(self):
        pass
        # _name = Schema._parseName("Foo")
        # self.assertIsInstance(_name, str)
        # self.assertEqual(_name, "Foo")

    @unittest.skip("Not yet implemented")
    def test_parseDBName(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_parseTableName(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_parseTableSchemaName(self):
        pass


if __name__ == '__main__':
    unittest.main()
