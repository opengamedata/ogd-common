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

class test_DatasetKey(TestCase):
    """Testbed for the DatasetSchema class.

        TODO : Test cases for empty details
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.test_schema = DatasetKey(raw_key="GAME_NAME_20250101_to_20250131")

    @staticmethod
    def RunAll():
        pass

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

if __name__ == '__main__':
    unittest.main()
