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

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class BasicInitCase(TestCase):
    """Testbed for the Schema base class.

    Because this is a base class, there are a limited number of functions worth testing directly.
    We implement a local TestSchema class that simply gives empty implementations of the abstract functions.
    """
    class TestSchema(Schema):
        def __init__(self, name:str, other_elements:Optional[Dict[str, Any]]=None):
            super().__init__(name=name, other_elements=other_elements)

        @property
        def AsMarkdown(self) -> str:
            return self.Name
    
        @classmethod
        def Default(cls) -> "BasicInitCase.TestSchema":
            return BasicInitCase.TestSchema(name="DefaultTestSchema", other_elements={})

        @classmethod
        def _fromDict(cls, name:str, all_elements:Dict[str, Any])-> "BasicInitCase.TestSchema":
            return BasicInitCase.TestSchema(name=name, other_elements=all_elements)

    @classmethod
    def setUpClass(cls) -> None:
        _elems = {
            "foo":1,
            "bar":"baz",
            "fizz":datetime.datetime(year=2020, month=1, day=1, hour=3, minute=4, second=5)
        }
        cls.test_schema = BasicInitCase.TestSchema(name="Test Schema", other_elements=_elems)

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
