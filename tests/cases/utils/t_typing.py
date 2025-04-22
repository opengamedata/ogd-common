# import libraries
import datetime
import logging
import unittest
from typing import Any, Dict, Optional
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.utils.typing import conversions
from tests.config.t_config import settings

_testing_cfg = TestConfig.FromDict(name="conversionsTestConfig", unparsed_elements=settings)
_level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
Logger.std_logger.setLevel(_level)

class Capitalize(TestCase):
    def test_normal_string(self):
        _str = conversions.Capitalize(value="fOo")
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "FOO")
    def test_nonstring(self):
        _str = conversions.Capitalize(value=100)
        self.assertIsInstance(_str, int)
        self.assertEqual(_str, 100)

class parseString(TestCase):
    def test_normal_string(self):
        _str = conversions._parseString(name="ParseStringVal", value="Foo")
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_wrongtype(self):
        _not_str = conversions._parseString(name="ParseStringVal", value=123)
        self.assertIsInstance(_not_str, str)
        self.assertEqual(_not_str, "123")

if __name__ == '__main__':
    unittest.main()
