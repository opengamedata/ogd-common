# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.events.DataElementSchema import DataElementSchema
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class EmptyCase(TestCase):
    """DataTableConfig test case where no initialization is used at class level.

    Fixture:
    * No initialization of a DataTableConfig object

    Case Categories:
    * Loading functions.
        * Appropriate here since the fixture doesn't set up an object.
    """

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
        _schema = DataElementSchema.FromDict(name="available_buildings Schema", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "available_buildings Schema")
        self.assertIsInstance(_schema.ElementType, str)
        self.assertEqual(_schema.ElementType, "List[Dict]")
        self.assertIsInstance(_schema.Description, str)
        self.assertEqual(_schema.Description, "The buildings available for the player to construct")
        self.assertIsInstance(_schema.Details, dict)
        self.assertEqual(_schema.Details, { "name":"str", "price":"int" })
