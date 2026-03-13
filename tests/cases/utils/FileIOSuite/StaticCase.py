"""FileIO test suite.

This module contains only static members, so we use a StaticCase, with one class per function tested.
"""
import logging
import os
import traceback
import unittest
from pathlib import Path
from unittest import TestCase
# local import(s)
from ogd.common.utils import fileio

class loadJSONFileCase(TestCase):
    def test_loadJSONFile(self):
        json_content = fileio.loadJSONFile(filename="test_fileio.json", path=Path("./tests/data/utils/"))
        self.assertIn("first", json_content.keys())
        self.assertEqual(json_content['first'], "the worst")
        self.assertIn("second", json_content.keys())
        self.assertEqual(json_content['second'], ["the best", "born, second place"])
        self.assertIn("fourth", json_content.keys())
        fourth = json_content['fourth']
        self.assertIn("a", fourth.keys())
        self.assertEqual(fourth['a'], "why's it out of order?")
        self.assertIn("b", fourth.keys())
        self.assertEqual(fourth['b'], 4)
        self.assertIn("c", fourth.keys())
        self.assertEqual(fourth['c'], False)

class openZipFromURLCase(TestCase):
    @unittest.skip("Not implemented")
    def test_openZipFromURL(self):
        pass

class openZipFromPathCase(TestCase):
    @unittest.skip("Not implemented")
    def test_openZipFromPath(self):
        pass

class readCSVFromPathCase(TestCase):
    @unittest.skip("Not implemented")
    def test_readCSVFromPath(self):
        pass

class getZippedLogDFbyURLCase(TestCase):
    @unittest.skip("Not implemented")
    def test_getZippedLogDFbyURL(self):
        pass

class getLogDFbyPathCase(TestCase):
    @unittest.skip("Not implemented")
    def test_getLogDFbyPath(self):
        pass
