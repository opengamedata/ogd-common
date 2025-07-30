# import libraries
import logging
import unittest
from unittest import TestCase
# import 3rd-party libraries
from google.cloud import bigquery
# import ogd libraries.
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.utils.Logger import Logger
# import locals
from tests.config.t_config import settings

class test_BigQueryConnector(TestCase):
    """Testbed for the GameStoreConfig class.

        TODO : Test more 'enabled' options/combinations.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg : TestConfig = TestConfig.FromDict(name="BQTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        _elems = {
            "DB_TYPE"    : "BIGQUERY",
            "PROJECT_ID" : "wcer-field-day-ogd-1798",
            "PROJECT_KEY": "./tests/config/ogd.json"
        }
        config = BigQueryConfig.FromDict(name="OPENGAMEDATA_BQ", unparsed_elements=_elems)
        cls.test_connector = BigQueryConnector(config=config)

    @staticmethod
    def RunAll():
        pass

    def test_Open(self):
        success = self.test_connector.Open()
        self.assertIsInstance(success, bool)
        self.assertTrue(success)

    def test_Close(self):
        self.test_connector.Open()
        success = self.test_connector.Close()
        self.assertIsInstance(success, bool)
        self.assertTrue(success)

    def test_IsOpen(self):
        success = self.test_connector.Open()
        is_open = self.test_connector.IsOpen
        self.assertIsInstance(is_open, bool)
        self.assertEqual(is_open, success)

    def test_Client(self):
        client = self.test_connector.Client
        self.assertIsNone(client)
        self.test_connector.Open()
        client = self.test_connector.Client
        self.assertIsInstance(client, bigquery.Client)

if __name__ == '__main__':
    unittest.main()
