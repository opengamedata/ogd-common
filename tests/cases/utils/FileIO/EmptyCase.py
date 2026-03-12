import logging
import os
import traceback
import unittest
from pathlib import Path
from unittest import TestCase
# local import(s)
from ogd.common.utils import fileio

class EmptyCase(TestCase):
    """FileIO test case where no initialization is used, on account of FileIO not being a class, just a module of functions (and a client class for API).

    Fixture:
    * No initialization of a FileIO

    Case Categories:
    * Loading functions.
        * Appropriate here since the fixture doesn't set up an object.
    """
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

    @unittest.skip("Not implemented")
    def test_openZipFromURL(self):
        pass

    @unittest.skip("Not implemented")
    def test_openZipFromPath(self):
        pass

    @unittest.skip("Not implemented")
    def test_readCSVFromPath(self):
        pass

    @unittest.skip("Not implemented")
    def test_getZippedLogDFbyURL(self):
        pass

    @unittest.skip("Not implemented")
    def test_getLogDFbyPath(self):
        pass
