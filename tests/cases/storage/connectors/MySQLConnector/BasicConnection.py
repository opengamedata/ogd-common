# import libraries
import logging
import unittest
from unittest import TestCase
# import 3rd-party libraries
from mysql.connector import connection
# import ogd libraries.
from ogd.common.configs.storage.MySQLConfig import MySQLConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.storage.connectors.MySQLConnector import MySQLConnector
from ogd.common.utils.Logger import Logger
# import locals
from tests.config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="MySQLTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class test_MySQLConnector(TestCase):
    """Testbed for the MySQLConnector class.

    Fixture:
    * Open a connection to BQ with basic configuration
    
    Case Categories:
    * Connection management functions
    """

    def setUp(self) -> None:
        config = MySQLConfig.FromDict(
            name="MYSQL_TEST_CONFIG",
            unparsed_elements=settings.get("MYSQL_TEST_CONFIG", {})
        )
        self.test_connector = MySQLConnector(config=config)
        self.test_connector.Open(writeable=False)

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
