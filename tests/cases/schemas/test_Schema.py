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
from src.ogd.common.schemas.Schema import Schema
from tests.config.t_config import settings

class test_Schema(TestCase):
    """Testbed for the Schema base class.

    Because this is a base class, there are a limited number of functions worth testing directly.
    We implement a local TestSchema class that simply gives empty implementations of the abstract functions.
    """
    class TestSchema(Schema):
        def __init__(self, name:str, other_elements:Optional[Dict[str, Any]]):
            super().__init__(name=name, other_elements=other_elements)

        @property
        def AsMarkdown(self) -> str:
            return self.Name
    
        @classmethod
        def Default(cls) -> "test_Schema.TestSchema":
            return test_Schema.TestSchema(name="DefaultTestSchema", other_elements={})

        @classmethod
        def _fromDict(cls, name:str, all_elements:Dict[str, Any])-> "test_Schema.TestSchema":
            return test_Schema.TestSchema(name=name, other_elements=all_elements)

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        _str_level =       "DEBUG" if _testing_cfg.Verbose else "INFO"
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        _elems = {
            "foo":1,
            "bar":"baz",
            "fizz":datetime.datetime(year=2020, month=1, day=1, hour=3, minute=4, second=5)
        }
        cls.test_schema = test_Schema.TestSchema(name="Test Schema", other_elements=_elems)

    @staticmethod
    def RunAll():
        pass

    # *** Tests using Schema directly

    def test_ParseElement_single_key(self):
        _elems = {
            "foo":1,
            "bar":2,
        }
        _elems_to_check = ["foo"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 1)
        _elems_to_check = ["bar"]
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 2)

    def test_ParseElement_two_keys(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["foo", "bar"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 1)
        _elems_to_check = ["bar", "foo"]
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 2)

    def test_ParseElement_two_keys_skip_first(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["fizz", "foo"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 1)

    def test_ParseElement_with_remove(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["baz"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, default_value=_default_val, remove_target=True)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 3)
        self.assertFalse("baz" in _elems)

    def test_ParseElement_two_types(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["foo"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=[int, str], default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 1)

    def test_ParseElement_two_types_use_second(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["foo"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=[str, int], default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 1)

    def test_ParseElement_change_type(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["foo"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=str, default_value=_default_val)
        self.assertIsInstance(_elem, str)
        self.assertEqual(_elem, "1")

    def test_ParseElement_two_types_change_to_first(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["foo"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=[bool, str], default_value=_default_val)
        self.assertIsInstance(_elem, bool)
        self.assertEqual(_elem, True)

    def test_ParseElement_use_default(self):
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["fizz"]
        _default_val = 0
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, default_value=_default_val)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 0)

    # *** Tests using TestSchema local implementation class ***

    def test_str(self):
        _str = str(self.test_schema)
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "TestSchema[Test Schema]")

    def test_repr(self):
        _repr = str(self.test_schema)
        self.assertIsInstance(_repr, str)
        self.assertEqual(_repr, "TestSchema[Test Schema]")

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Test Schema")

    def test_NonStandardElements(self):
        _elems = {
            "foo":1,
            "bar":"baz",
            "fizz":datetime.datetime(year=2020, month=1, day=1, hour=3, minute=4, second=5)
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    def test_NonStandardElementNames(self):
        _elem_names = ["foo", "bar", "fizz"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)

if __name__ == '__main__':
    unittest.main()
