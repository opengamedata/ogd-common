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

class BasicInitCase(TestCase):
    """DataElementSchema test case where basic initialization is used.
    
    Fixture:
    * Initialize a `DataElementSchema` object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions
        * Check that we get back exactly the hardcoded values we passed in to the `__init__(...)` function.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `DataElementSchema` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        cls.test_schema = DataElementSchema(
            name="available_building Schema",
            element_type="List[Dict]",
            description="The buildings available for the player to construct",
            details={
                "name":"str",
                "price":"int"
            },
            other_elements={ "foo":"bar" }
        )

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "available_building Schema")

    def test_ElementType(self):
        _str = self.test_schema.ElementType
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "List[Dict]")

    def test_Description(self):
        _str = self.test_schema.Description
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "The buildings available for the player to construct")

    def test_Details(self):
        _details = self.test_schema.Details
        self.assertIsInstance(_details, dict)
        _dict = {
            "name":"str",
            "price":"int"
        }
        self.assertEqual(_details, _dict)

    def test_NonStandardElements(self):
        _elems = {
            "foo":"bar"
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    def test_NonStandardElementNames(self):
        _elem_names = ["foo"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)
