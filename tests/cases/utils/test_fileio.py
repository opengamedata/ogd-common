import logging
import os
import traceback
import unittest
from pathlib import Path
from unittest import TestCase
# local import(s)
from ogd.common.utils import fileio

class test_fileio(TestCase):
    def RunAll(self):
        self.test_loadJSONFile()
        print("Ran all test_fileio tests.")

    def test_loadJSONFile(self):
        json_content = fileio.loadJSONFile(filename="test_fileio.json", path=Path("./tests/cases/utils/"))
        self.assertEqual(json_content['first'], "the worst")
        self.assertEqual(json_content['second'], ["the best", "born, second place"])
        self.assertTrue("fourth" in json_content.keys())
        self.assertEqual(json_content['fourth']['a'], "why's it out of order?")
        self.assertEqual(json_content['fourth']['b'], 4)
        self.assertEqual(json_content['fourth']['c'], False)
