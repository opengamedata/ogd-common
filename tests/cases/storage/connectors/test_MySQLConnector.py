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

class test_MySQLConnector(TestCase):
    """Testbed for the GameStoreConfig class.

        TODO : Test more 'enabled' options/combinations.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg : TestConfig = TestConfig.FromDict(name="MySQLTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        _elems = settings.get("MYSQL_TEST_CONFIG", {})
        config = MySQLConfig.FromDict(name="MYSQL_TEST_CONFIG", unparsed_elements=_elems)
        cls.test_connector = MySQLConnector(config=config)

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

    def test_Connection(self):
        client = self.test_connector.Connection
        self.assertIsNone(client)
        self.test_connector.Open()
        client = self.test_connector.Connection
        self.assertIsInstance(client, connection.MySQLConnection)

if __name__ == '__main__':
    unittest.main()
