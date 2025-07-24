# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.configs.TestConfig import TestConfig as TestConfigLocal
from tests.config.t_config import settings

class test_TestConfig(TestCase):
    """Testbed for the GameStoreConfig class.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        _enabled = {
            "INTERFACES":False,
            "SCHEMAS":True,
            "UTILS":True
        }
        cls.test_schema = TestConfigLocal(
            name="Local Test Config Schema",
            verbose=True,
            enabled_tests=_enabled,
            other_elements={ "foo":"bar" }
        )

    @staticmethod
    def RunAll():
        pass

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Local Test Config Schema")

    def test_Verbose(self):
        _str = self.test_schema.Verbose
        self.assertIsInstance(_str, bool)
        self.assertEqual(_str, True)

    def test_EnabledTests(self):
        _enabled = {
            "INTERFACES":False,
            "SCHEMAS":True,
            "UTILS":True
        }
        _vals = self.test_schema.EnabledTests
        self.assertIsInstance(_vals, dict)
        self.assertEqual(_vals, _enabled)

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
            "VERBOSE" : False,
            "ENABLED" : {
                "INTERFACES":False,
                "SCHEMAS":True,
                "UTILS":True
            },
            "REMOTE_ADDRESS" : "127.0.0.1:5000"
        }
        _enabled = {
            "INTERFACES":False,
            "SCHEMAS":True,
            "UTILS":True
        }
        _schema = TestConfigLocal.FromDict(name="Local Test Config Schema", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "Local Test Config Schema")
        self.assertIsInstance(_schema.Verbose, bool)
        self.assertEqual(_schema.Verbose, False)
        self.assertIsInstance(_schema.EnabledTests, dict)
        self.assertEqual(_schema.EnabledTests, _enabled)

    @unittest.skip("Not yet implemented")
    def test_parseLocalDir(self):
        pass
        # _name = Schema._parseName("Foo")
        # self.assertIsInstance(_name, str)
        # self.assertEqual(_name, "Foo")

    @unittest.skip("Not yet implemented")
    def test_parseRemoteURL(self):
        pass

    @unittest.skip("Not yet implemented")
    def test_parseTemplatesURL(self):
        pass

if __name__ == '__main__':
    unittest.main()
