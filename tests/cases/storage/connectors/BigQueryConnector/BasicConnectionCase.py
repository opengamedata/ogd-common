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

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="BQTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class BasicConnectionCase(TestCase):
    """Testbed for the BigQueryConnector class.

    Fixture:
    * Open a connection to BQ with basic configuration
    
    Case Categories:
    * Connection management functions
    """

    @classmethod
    def setUp(self) -> None:
        """Set up the testbed.
        """
        _elems = {
            "DB_TYPE"    : "BIGQUERY",
            "PROJECT_ID" : "wcer-field-day-ogd-1798",
            "PROJECT_KEY": "./tests/config/ogd.json"
        }
        config = BigQueryConfig.FromDict(name="OPENGAMEDATA_BQ", unparsed_elements=_elems)
        self.test_connector = BigQueryConnector(config=config)
        self.test_connector.Open()

    def test_Close(self):
        self.test_connector.Open()
        success = self.test_connector.Close()
        self.assertIsInstance(success, bool)
        self.assertTrue(success)

    def test_IsOpen(self):
        is_open = self.test_connector.IsOpen
        self.assertIsInstance(is_open, bool)
        self.assertEqual(is_open, True)

if __name__ == '__main__':
    unittest.main()
