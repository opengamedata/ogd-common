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

class parseList(TestCase):
    def test_normal_list(self):
        _elems = [1, 2.2, "3"]
        _list = conversions._parseList(name="parseListVal", value=_elems)
        self.assertIsInstance(_list, list)
        self.assertEqual(_list, _elems)

    def test_dictstring(self):
        _elems = [1, 2.2, "3"]
        _elems_str = '[1, 2.2, "3"]'
        _list = conversions._parseList(name="parseListVal", value=_elems_str)
        self.assertIsInstance(_list, list)
        self.assertEqual(_list, _elems)

    def test_nullstring(self):
        with self.subTest(msg="_parseList: string = ''"):
            _str = ""
            _list = conversions._parseList(name="parseListVal", value=_str)
            self.assertIsNone(_list)
        with self.subTest(msg="_parseList: string = 'None'"):
            _str = "None"
            _list = conversions._parseList(name="parseListVal", value=_str)
            self.assertIsNone(_list)

    def test_nonlist(self):
        _val = 42
        _list = conversions._parseList(name="parseListVal", value=_val)
        self.assertIsNone(_list)

    def test_bad_liststring(self):
        _elems = "['foo', bar]"
        _list = conversions._parseList(name="parseListVal", value=_elems)
        self.assertIsNone(_list)

class parseJSON(TestCase):
    def test_normal_dict(self):
        _elems = {
            "foo":1,
            "bar":2.2,
            "baz":"3"
        }
        _dict = conversions._parseJSON(name="parseJSONVal", value=_elems)
        self.assertIsInstance(_dict, dict)
        self.assertEqual(_dict, _elems)

    def test_dictstring(self):
        _elems = {
            "foo":1,
            "bar":2.2,
            "baz":"3"
        }
        _elems_str = '''{
            "foo":1,
            "bar":2.2,
            "baz":"3"
        }'''
        _dict = conversions._parseJSON(name="parseJSONVal", value=_elems_str)
        self.assertIsInstance(_dict, dict)
        self.assertEqual(_dict, _elems)

    def test_nullstring(self):
        with self.subTest(msg="_parseJSON: string = ''"):
            _str = ""
            _dict = conversions._parseJSON(name="parseJSONVal", value=_str)
            self.assertIsNone(_dict)
        with self.subTest(msg="_parseJSON: string = 'None'"):
            _str = "None"
            _dict = conversions._parseJSON(name="parseJSONVal", value=_str)
            self.assertIsNone(_dict)

    def test_nondict(self):
        _val = 42
        _dict = conversions._parseJSON(name="parseJSONVal", value=_val)
        self.assertIsNone(_dict)

    def test_bad_dictstring(self):
        _elems = "{ 'foo':bar }"
        _dict = conversions._parseJSON(name="parseJSONVal", value=_elems)
        self.assertIsNone(_dict)

if __name__ == '__main__':
    unittest.main()
