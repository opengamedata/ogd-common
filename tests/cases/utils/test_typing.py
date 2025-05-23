# import libraries
import datetime
import logging
import unittest
from pathlib import Path
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

@unittest.skip("Not Implemented")
class ConvertToType(TestCase):
    def test_null_values(self):
        pass

@unittest.skip("Not Implemented")
class ToBool(TestCase):
    def test_normal_bool(self):
        pass

class ToInt(TestCase):
    def test_normal_int(self):
        _int = conversions.ToInt(name="ParseIntVal", value=1)
        self.assertIsInstance(_int, int)
        self.assertEqual(_int, 1)

    def test_float_to_int(self):
        with self.subTest(msg="_parseInt: Round float up"):
            _int = conversions.ToInt(name="ParseIntVal", value=1.75)
            self.assertIsInstance(_int, int)
            self.assertEqual(_int, 2)
        with self.subTest(msg="_parseInt: Round float up at edge case"):
            _int = conversions.ToInt(name="ParseIntVal", value=1.5)
            self.assertIsInstance(_int, int)
            self.assertEqual(_int, 2)
        with self.subTest(msg="_parseInt: Round float down"):
            _int = conversions.ToInt(name="ParseIntVal", value=1.25)
            self.assertIsInstance(_int, int)
            self.assertEqual(_int, 1)

    def test_wrongtype(self):
        _nan = {1:2}
        _int = conversions.ToInt(name="ParseIntVal", value=_nan)
        self.assertIsNone(_int)

class ToFloat(TestCase):
    def test_normal_float(self):
        _float = conversions.ToFloat(name="ParseFloatVal", value=1.2)
        self.assertIsInstance(_float, float)
        self.assertEqual(_float, 1.2)

    def test_int_to_float(self):
        _float = conversions.ToFloat(name="ParseFloatVal", value=1)
        self.assertIsInstance(_float, float)
        self.assertEqual(_float, 1.)

    def test_wrongtype(self):
        _nan = {1:2}
        _float = conversions.ToFloat(name="ParseFloatVal", value=_nan)
        self.assertIsNone(_float)

class ToString(TestCase):
    def test_normal_string(self):
        _str = conversions.ToString(name="ParseStringVal", value="Foo")
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

    def test_int_to_str(self):
        _str = conversions.ToString(name="ParseStringVal", value=123)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "123")

    def test_dict_to_str(self):
        _elem = {1:2}
        _elem_str = "{1: 2}"
        _str = conversions.ToString(name="ParseStringVal", value=_elem)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, _elem_str)

class ToPath(TestCase):
    def test_normal_path(self):
        _val = Path("./Foo")
        _path = conversions.ToPath(name="ParsePathVal", value=_val)
        self.assertIsInstance(_path, Path)
        self.assertEqual(_path, _val)

    def test_pathstring(self):
        _elem = Path("./Foo")
        _elem_str = "./Foo"
        _path = conversions.ToPath(name="ParsePathVal", value=_elem_str)
        self.assertIsInstance(_path, Path)
        self.assertEqual(_path, _elem)

    def test_wrongtype(self):
        _not_path = conversions.ToPath(name="ParseStringVal", value=123)
        self.assertIsNone(_not_path)

@unittest.skip(reason="Not implemented")
class ToDatetime(TestCase):
    def test_normal_timezone(self):
        _val = datetime.datetime(2020, 1, 1)
        _str = conversions.ToDatetime(name="ToDatetimeVal", value=_val)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

@unittest.skip(reason="Not implemented")
class ToTimedelta(TestCase):
    def test_normal_timezone(self):
        _val = datetime.timedelta(hours=1)
        _str = conversions.ToTimedelta(name="ToTimedeltaVal", value=_val)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

@unittest.skip(reason="Not implemented")
class ToTimezone(TestCase):
    def test_normal_timezone(self):
        _val = datetime.timezone(datetime.timedelta(hours=1))
        _str = conversions.ToTimezone(name="ToTimezoneVal", value=_val)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Foo")

class ToList(TestCase):
    def test_normal_list(self):
        _elems = [1, 2.2, "3"]
        _list = conversions.ToList(name="ToListVal", value=_elems)
        self.assertIsInstance(_list, list)
        self.assertEqual(_list, _elems)

    def test_dictstring(self):
        _elems = [1, 2.2, "3"]
        _elems_str = '[1, 2.2, "3"]'
        _list = conversions.ToList(name="ToListVal", value=_elems_str)
        self.assertIsInstance(_list, list)
        self.assertEqual(_list, _elems)

    def test_nullstring(self):
        with self.subTest(msg="ToList: string = 'None'"):
            _str = "None"
            _list = conversions.ToList(name="ToListVal", value=_str)
            self.assertIsNone(_list)
        with self.subTest(msg="ToList: string = 'null'"):
            _str = "null"
            _list = conversions.ToList(name="ToListVal", value=_str)
            self.assertIsNone(_list)
        with self.subTest(msg="ToList: string = ''"):
            _str = ""
            _list = conversions.ToList(name="ToListVal", value=_str)
            self.assertIsNone(_list)

    def test_nonlist(self):
        _val = 42
        _list = conversions.ToList(name="ToListVal", value=_val)
        self.assertIsNone(_list)

    def test_bad_liststring(self):
        _elems = "['foo', bar]"
        _list = conversions.ToList(name="ToListVal", value=_elems)
        self.assertIsNone(_list)

class ToJSON(TestCase):
    def test_normal_dict(self):
        _elems = {
            "foo":1,
            "bar":2.2,
            "baz":"3"
        }
        _dict = conversions.ToJSON(name="ToJSONVal", value=_elems)
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
        _dict = conversions.ToJSON(name="ToJSONVal", value=_elems_str)
        self.assertIsInstance(_dict, dict)
        self.assertEqual(_dict, _elems)

    def test_nullstring(self):
        with self.subTest(msg="ToJSON: string = 'None'"):
            _str = "None"
            _dict = conversions.ToJSON(name="ToJSONVal", value=_str)
            self.assertIsNone(_dict)
        with self.subTest(msg="ToJSON: string = 'null'"):
            _str = "null"
            _dict = conversions.ToJSON(name="ToJSONVal", value=_str)
            self.assertIsNone(_dict)
        with self.subTest(msg="ToJSON: string = ''"):
            _str = ""
            _dict = conversions.ToJSON(name="ToJSONVal", value=_str)
            self.assertIsNone(_dict)

    def test_nondict(self):
        _val = 42
        _dict = conversions.ToJSON(name="ToJSONVal", value=_val)
        self.assertIsNone(_dict)

    def test_bad_dictstring(self):
        _elems = "{ 'foo':bar }"
        _dict = conversions.ToJSON(name="ToJSONVal", value=_elems)
        self.assertIsNone(_dict)

if __name__ == '__main__':
    unittest.main()
