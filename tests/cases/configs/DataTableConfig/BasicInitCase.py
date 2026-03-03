# import libraries
import logging
import unittest
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

class BasicInitCase(TestCase):
    """DataTableConfig test case where basic initialization is used.
    
    Fixture:
    * Initialize a DataTableConfig object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions.
        * Appropriate for this case, since we are hardcoding initial values and can then test we get them back directly.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.test_schema = DataTableConfig(
            name="Game Source Schema",
            store="AQUALAB_BQ",
            table_schema="OPENGAMEDATA_BIGQUERY",
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
        _str = self.test_schema.StoreName
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
