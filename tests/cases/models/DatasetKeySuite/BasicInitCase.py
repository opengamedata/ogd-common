# import libraries
import logging
import unittest
from datetime import date
from pathlib import Path
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.models.DatasetKey import DatasetKey
from tests.config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class BasicInitCase(TestCase):
    """DatasetKey test case where basic initialization is used.
    
    Fixture:
    * Initialize a DatasetKey object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions.
        * Appropriate for this case, since we are hardcoding initial values and can then test we get them back directly.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `Feature` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        cls.test_schema = DatasetKey(game_id="GAME_NAME", from_date="20250101", to_date="20250131")

    def test_GameID(self):
        _str = self.test_schema.GameID
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "GAME_NAME")

    def test_DateFrom(self):
        _date = self.test_schema.DateFrom
        self.assertIsInstance(_date, date)
        self.assertEqual(_date, date(year=2025, month=1, day=1))

    def test_DateTo(self):
        _date = self.test_schema.DateTo
        self.assertIsInstance(_date, date)
        self.assertEqual(_date, date(year=2025, month=1, day=31))

    def test_FromString(self):
        _schema = DatasetKey.FromString("GAME_NAME_20250101_to_20250131")
        self.assertEqual(_schema.GameID, self.test_schema.GameID)
        self.assertEqual(_schema.DateFrom, self.test_schema.DateFrom)
        self.assertEqual(_schema.DateTo, self.test_schema.DateTo)
