# import libraries
import logging
import unittest
from datetime import date
from pathlib import Path
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from tests.config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class EmptyCase(TestCase):
    """DatasetSChema test case where no initialization is used at class level.

    Fixture:
    * No initialization of a DatasetSChema object

    Case Categories:
    * Loading functions.
        * Appropriate here since the fixture doesn't set up an object.
    * Parsing functions. 
        * We test these so as to get details of where loading fails.
    """

    @unittest.skip("Not Implemented")
    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
               "type" : "List[Dict]",
               "details": {
                  "name":"str",
                  "price":"int"
               },
               "description" : "The buildings available for the player to construct"
        }
        _schema = DatasetSchema.FromDict(name="available_buildings Schema", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "available_buildings Schema")
