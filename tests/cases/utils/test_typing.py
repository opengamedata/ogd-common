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
from src.ogd.common.utils.typing import *
from tests.config.t_config import settings

class test_conversions(TestCase):
    @staticmethod
    def RunAll():
        pass

    def test_parseString(self):
        _str = conversions._parseString(name="ParseStringVal", value="Foo")
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_parseString_wrongtype(self):
        _not_str = conversions._parseString(name="ParseStringVal", value=123)
        self.assertIsInstance(_not_str, str)
        self.assertEqual(_not_str, "123")

if __name__ == '__main__':
    unittest.main()
