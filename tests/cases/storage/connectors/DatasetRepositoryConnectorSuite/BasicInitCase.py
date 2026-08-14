# import libraries
import logging
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.storage.connectors.DatasetRepositoryConnector import DatasetRepositoryConnector
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.utils.Logger import Logger
# import locals
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="MySQLTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class BasicInitCase(TestCase):
    """Testbed for the MySQLConnector class.

    Fixture:
    * Open a connection to BQ with basic configuration
    
    Case Categories:
    * Connection management functions
    """

    def setUp(self) -> None:
        config = DirectoryLocationConfig(name="TestLocation", folder_path="tests/data/storage/connectors/")
        self.test_connector = DatasetRepositoryConnector(config=config)
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
