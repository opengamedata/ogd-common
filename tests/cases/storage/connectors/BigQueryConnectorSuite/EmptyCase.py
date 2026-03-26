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
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="BQTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class test_BigQueryConnector(TestCase):
    """Testbed for the BigQueryConnector class.

    Fixture:
    * Initialized but non-opened a BigQueryConnector object.
    
    Case Categories:
    * Connection opening function
    """

    def setUp(self) -> None:
        _elems = {
            "DB_TYPE"    : "BIGQUERY",
            "PROJECT_ID" : "wcer-field-day-ogd-1798",
            "PROJECT_KEY": "./tests/config/ogd.json"
        }
        config = BigQueryConfig.FromDict(name="OPENGAMEDATA_BQ", unparsed_elements=_elems)
        self.test_connector = BigQueryConnector(config=config)

    def test_Open(self):
        # Pre-check
        self.assertIsNone(self.test_connector.Client)

        # Test stimulus
        success = self.test_connector.Open()

        # Post-checks
        self.assertIsInstance(success, bool)
        self.assertTrue(success)
        self.assertIsInstance(self.test_connector.Client, bigquery.Client)
