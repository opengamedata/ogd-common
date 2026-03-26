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

class BasicInitCase(TestCase):
    """TestConfig test case where basic initialization is used.
    
    Fixture:
    * Initialize a TestConfig object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions.
        * Appropriate for this case, since we are hardcoding initial values and can then test we get them back directly.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `TestConfig` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
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
