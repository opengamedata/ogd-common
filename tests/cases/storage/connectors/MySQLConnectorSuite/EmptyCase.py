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
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class EmptyCase(TestCase):
    """Testbed for the MySQLConnector class.

    Fixture:
    * Initialized but non-opened a BigQueryConnector object.
    
    Case Categories:
    * Connection opening function
    """

    @classmethod
    def setUp(self) -> None:
        config = MySQLConfig.FromDict(
            name="MYSQL_TEST_CONFIG",
            unparsed_elements=settings.get("MYSQL_TEST_CONFIG", {})
        )
        self.test_connector = MySQLConnector(config=config)

    @unittest.skip("Skipping until we determine a good way to guarantee there's something to connect to in testing environment.")
    def test_Open(self):
        # Pre-check
        self.assertIsNone(self.test_connector.Connection)

        # Test stimulus
        success = self.test_connector.Open(writeable=False)

        # Post-checks
        self.assertIsInstance(success, bool)
        self.assertTrue(success)
        self.assertIsInstance(self.test_connector.Connection, connection.MySQLConnection)
