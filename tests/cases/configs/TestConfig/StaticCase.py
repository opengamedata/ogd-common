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

class StaticCase(TestCase):
    """TestConfig test case to check that all loading and parsing functions work correctly.

    The test fixture here is technically "empty", since we don't define any data initially.
    We're ultimately just testing all the static functions here, and the name "static" is slightly more descriptive than "empty," hence StaticCase.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

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
