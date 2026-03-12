# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.events.GameStateSchema import GameStateSchema
from tests.config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

@unittest.skip("Not implemented")
class BasicInitCase(TestCase):
    """DataTableConfig test case where basic initialization is used.

    TODO : Implement and enable tests.
    
    Fixture:
    * Initialize a `DataTableConfig` object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions
        * Check that we get back exactly the hardcoded values we passed in to the `__init__(...)` function.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `GameStateSchema` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        cls.test_schema = GameStateSchema(
            name="available_building Schema",
            game_state={},
            other_elements={ "foo":"bar" }
        )

    @unittest.skip("Not implemented")
    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "available_building Schema")

    @unittest.skip("Not implemented")
    def test_Description(self):
        pass
        # _str = self.test_schema.ElementType
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "List[Dict]")

    @unittest.skip("Not implemented")
    def test_EventData(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_NonStandardElements(self):
        _elems = {
            "foo":"bar"
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    @unittest.skip("Not implemented")
    def test_NonStandardElementNames(self):
        _elem_names = ["foo"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)
