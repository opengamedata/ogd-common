# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.events.LoggingSpecificationSchema import LoggingSpecificationSchema
from tests.config.t_config import settings

@unittest.skip("Not implemented")
class test_LoggingSpecificationSchema(TestCase):
    """Testbed for the LoggingSpecificationSchema class.

        TODO : Implement and enable tests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.test_schema = LoggingSpecificationSchema(
            name="available_building Schema", game_id="", enum_defs={},
            game_state={}, user_data={}, event_list=[],
            logging_version=1,
            other_elements={ "foo":"bar" }
        )

    @staticmethod
    def RunAll():
        pass

    @unittest.skip("Not implemented")
    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "available_building Schema")

    @unittest.skip("Not implemented")
    def test_GameName(self):
        pass
        # _str = self.test_schema.ElementType
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "List[Dict]")

    @unittest.skip("Not implemented")
    def test_EnumDefs(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_GameState(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_UserData(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_Events(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_EventTypes(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_Detectors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_DetectorNames(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_IteratedDetectors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_AggregateDetectors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_Features(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_FeatureNames(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_LegacyPerLevelFeatures(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_IteratedExtractors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_AggregateExtractors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_LevelRange(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_OtherRanges(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_Config(self):
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

    @unittest.skip("Not implemented")
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
        _schema = LoggingSpecificationSchema.FromDict(name="available_buildings Schema", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "available_buildings Schema")

if __name__ == '__main__':
    unittest.main()
