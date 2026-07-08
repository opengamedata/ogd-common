# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.configs.TestConfig import TestConfig as TestConfigLocal
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class EmptyCase(TestCase):
    """TestConfig test case where no initialization is used at class level.

    Fixture:
    * No initialization of a TestConfig object

    Case Categories:
    * Loading functions.
        * Appropriate here since the fixture doesn't set up an object.
    * Parsing functions. 
        * We test these so as to get details of where loading fails.
    """

    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "VERBOSE" : False,
            "REMOTE_ADDRESS" : "127.0.0.1:5000"
        }
        _schema = TestConfigLocal.FromDict(name="Local Test Config Schema", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "Local Test Config Schema")
        self.assertIsInstance(_schema.Verbose, bool)
        self.assertEqual(_schema.Verbose, False)

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
