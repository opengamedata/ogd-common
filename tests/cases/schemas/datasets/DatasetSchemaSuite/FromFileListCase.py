# import libraries
import logging
import unittest
from datetime import date
from pathlib import Path
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class BasicInitCase(TestCase):
    """DatasetSchema test case where we initialize with the structure used as standard in a file_list.json.
    
    Fixture:
    * Initialize a DatasetSchema object with hardcoded dict matching format of an old `file_list.json`
    
    Case Categories:
    * Property functions
        * Check that we get back exactly the equivalents to the hardcoded values we used in the dict.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `Feature` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        raw_data = {
            "ogd_revision": "882f4a5",
            "start_date": "06/01/2025",
            "end_date": "12/31/2025",
            "date_modified": "05/08/2026",
            "sessions": 22882,
            "population_file": "data/AQUALAB/AQUALAB_20250601_to_20251231_882f4a5_population-features.zip",
            "population_template": "",
            "players_file": "data/AQUALAB/AQUALAB_20250601_to_20251231_882f4a5_player-features.zip",
            "players_template": "",
            "sessions_file": "data/AQUALAB/AQUALAB_20250601_to_20251231_882f4a5_session-features.zip",
            "sessions_template": "",
            "events_file": None,
            "events_template": None,
            "all_events_file": None,
            "all_events_template": None
        }
        cls.test_schema = DatasetSchema.FromDict(name="AQUALAB", unparsed_elements=raw_data)

    def test_Key(self):
        _key = self.test_schema.Key
        self.assertIsInstance(_key, DatasetKey)
        self.assertEqual(str(_key), "AQUALAB_20250601_to_20251231")

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "AQUALAB")

    def test_OGDRevision(self):
        
        self.assertIsInstance(self.test_schema.OGDRevision, str)
        self.assertEqual(self.test_schema.OGDRevision, "882f4a5")
