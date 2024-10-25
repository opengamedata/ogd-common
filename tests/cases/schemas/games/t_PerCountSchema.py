# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.schemas.configs.TestConfigSchema import TestConfigSchema
from ogd.common.schemas.games.FeatureSchema import SubfeatureSchema
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.games.PerCountSchema import PerCountSchema
from tests.config.t_config import settings

class t_AggregateSchema(TestCase):
    """Testbed for the GameSourceSchema class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfigSchema.FromDict(name="SchemaTestConfig", all_elements=settings, logger=None)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        _elems = {
            "threshold": 30,
            "enabled": True,
            "type": "ActiveTime",
            "description": "Active time of a player",
            "return_type": "timedelta",
            "subfeatures": {
                "Seconds": {
                    "description": "The number of seconds of active time.",
                    "return_type": "int"
                }
            }
        }
        cls.test_schema = PerCountSchema(
            name="ActiveTime Schema",
            count=5,
            prefix="lvl",
            other_elements=_elems
        )

    @staticmethod
    def RunAll():
        pass

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "ActiveTime Schema")

    def test_TypeName(self):
        _str = self.test_schema.TypeName
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "ActiveTime")

    def test_Enabled(self):
        _enabled = self.test_schema.Enabled
        self.assertIsInstance(_enabled, bool)
        self.assertEqual(_enabled, True)

    def test_Description(self):
        _str = self.test_schema.Description
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Active time of a player")

    def test_ReturnType(self):
        _str = self.test_schema.ReturnType
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "timedelta")

    def test_Subfeatures(self):
        _feats = self.test_schema.Subfeatures
        seconds = _feats.get("Seconds")
        _ret  = "int"
        _desc = "The number of seconds of active time."
        self.assertIsInstance(_feats, dict)
        self.assertIsNotNone(seconds)
        if seconds is not None:
            self.assertEqual(seconds.Name, "Seconds")
            self.assertEqual(seconds.ReturnType, _ret)
            self.assertEqual(seconds.Description, _desc)

    def test_NonStandardElements(self):
        _elems = {
            "threshold":30
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    def test_NonStandardElementNames(self):
        _elem_names = ["threshold"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)

    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "threshold": 30,
            "enabled": True,
            "type": "ActiveTime",
            "description": "Active time of a player",
            "return_type": "timedelta",
            "subfeatures": {
                "Seconds": {
                    "description": "The number of seconds of active time.",
                    "return_type": "int"
                }
            }
        }
        _schema = PerCountSchema.FromDict(name="ActiveTime Schema", all_elements=_dict, logger=None)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "ActiveTime Schema")
        self.assertIsInstance(_schema.TypeName, str)
        self.assertEqual(_schema.TypeName, "ActiveTime")
        self.assertIsInstance(_schema.Enabled, bool)
        self.assertEqual(_schema.Enabled, True)
        self.assertIsInstance(_schema.Description, str)
        self.assertEqual(_schema.Description, "Active time of a player")
        self.assertIsInstance(_schema.ReturnType, str)
        self.assertEqual(_schema.Description, "timedelta")
        self.assertIsInstance(_schema.Subfeatures, dict)
        seconds = _schema.Subfeatures.get("Seconds")
        self.assertIsNotNone(seconds)
        if seconds is not None:
            self.assertEqual(seconds.Name, "Seconds")
            self.assertEqual(seconds.ReturnType, "int")
            self.assertEqual(seconds.Description, "The number of seconds of active time.")

if __name__ == '__main__':
    unittest.main()
