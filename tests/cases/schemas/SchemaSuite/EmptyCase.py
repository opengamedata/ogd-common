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
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class EmptyCase(TestCase):
    """Testbed for the Schema base class.

    Fixture:
    * No initialization of a Schema object. Because this is a base class, we can not initialize an instance in the first place.

    Case Categories:
    * Parsing functions. 
        * We test these so as to get details of where loading fails.
    """

    def test_ParseElement_single_key(self):
        """Test the `ParseElement` function with a single `valid_key`.
        """
        elems = {
            "foo":1,
            "bar":2,
        }
        elems_to_check = ["foo"]
        elem = Schema.ParseElement(unparsed_elements=elems, valid_keys=elems_to_check, to_type=int, default_value=0)
        self.assertIsInstance(elem, int)
        self.assertEqual(elem, 1)
        self.assertIn("foo", elems)
        self.assertIn("bar", elems)

    def test_ParseElement_single_key_remove(self):
        """Test the `ParseElement` function with a single `valid_key`, and removal of the matching element from the source dict.
        """
        elems = {
            "foo":1,
            "bar":2,
        }
        elems_to_check = ["bar"]
        elem = Schema.ParseElement(unparsed_elements=elems, valid_keys=elems_to_check, remove_target=True, to_type=int, default_value=0)
        self.assertIsInstance(elem, int)
        self.assertEqual(elem, 2)
        self.assertIn("foo", elems)
        self.assertNotIn("bar", elems)

    def test_ParseElement_two_keys(self):
        """Test the `ParseElement` function with multiple `valid_key`s, searching for the first to appear in the dict.
        """
        elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["foo", "bar"]
        elem = Schema.ParseElement(unparsed_elements=elems, valid_keys=_elems_to_check, to_type=int, default_value=0)
        self.assertIsInstance(elem, int)
        self.assertEqual(elem, 1)
        self.assertIn("foo", elems)
        self.assertIn("bar", elems)

    def test_ParseElement_two_keys_remove(self):
        """Test the `ParseElement` function with multiple `valid_key`s, searching for the first to appear in the dict, with removal of the matching element from the source dict.
        """
        _elems = {
            "foo":1,
            "bar":2,
            "baz":3
        }
        _elems_to_check = ["bar", "foo"]
        _elem = Schema.ParseElement(unparsed_elements=_elems, valid_keys=_elems_to_check, to_type=int, remove_target=True, default_value=0)
        self.assertIsInstance(_elem, int)
        self.assertEqual(_elem, 2)

    def test_ParseElement_two_keys_skip_first(self):
        """Test the `ParseElement` function with multiple `valid_key`s, searching for the first to appear in the dict, where the first key does not appear in the dict but the second does.
        """
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

    def test_ParseElement_two_types(self):
        """Test the `ParseElement` function with multiple `to_type` options.
        """
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
        """Test the `ParseElement` function with multiple `to_type` options, where the second option matches the type of the found element.
        """
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
        """Test the `ParseElement` function with a to_type that does not match the type of the found element, resulting in a type change.
        """
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
        """Test the `ParseElement` function  with multiple `to_type` options, where neither option matches the found element, resulting in a type change.
        """
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
        """Test the `ParseElement` function  with a key that does not match any in the dict, resulting in use of the default value.
        """
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