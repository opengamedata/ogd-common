# import libraries
import logging
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.storage.connectors.DatasetRepositoryConnector import DatasetRepositoryConnector
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.utils.Logger import Logger
# import locals
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="DatasetRepositoryConnectorTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class UnopenedRemoteCase(TestCase):
    """Testbed for the DatasetRepositoryConnector class.

    Fixture:
    * Initialized but non-opened a DatasetRepositoryConnector object.
    
    Case Categories:
    * Connection opening function
    """

    @classmethod
    def setUp(self) -> None:
        config = URLLocationConfig(name="TestLocation", url="https://opengamedata.fielddaylab.wisc.edu/data/file_list.json")
        self.test_connector = DatasetRepositoryConnector(repository_location=config)

    def test_Open(self):
        # Pre-check
        self.assertFalse(self.test_connector.IsOpen)

        # Test stimulus
        success = self.test_connector.Open(writeable=False)

        # Post-checks
        self.assertTrue(success)
        self.assertIsInstance(self.test_connector.StoreConfig, DatasetRepositoryConfig)
