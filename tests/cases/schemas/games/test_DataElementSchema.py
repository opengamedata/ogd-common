# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.games.DataElementSchema import DataElementSchema
from tests.config.t_config import settings

class test_DataElementSchema(TestCase):
    """Testbed for the GameSourceSchema class.

        TODO : Test cases for empty details
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
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

    @staticmethod
    def RunAll():
        pass

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

if __name__ == '__main__':
    unittest.main()
