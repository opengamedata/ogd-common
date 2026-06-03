# import libraries
import json
import logging
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.configs.locations.LocationConfig import LocationConfig
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class FromLegacyFileListCase(TestCase):
    """DatasetSchema test case where we initialize with the structure of a file_list.json as of ogd-core 0.0.14.
    
    Fixture:
    * Initialize a DatasetSchema object with hardcoded dict matching format of a `file_list.json` from ogd-core v0.0.14
    
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
        raw_json = {}
        with open("tests/data/schemas/datasets/legacy_file_list.json") as raw_file:
            raw_json = json.loads(raw_file.read())
        config = raw_json.get("CONFIG", {})
        raw_data = raw_json.get("AQUALAB",{}).get("AQUALAB_20260301_to_20260331")
        cls.test_schema = DatasetSchema.FromDict(name="AQUALAB", unparsed_elements=raw_data)
        cls.test_schema.BaseFileLocation = URLLocationConfig.FromString(name="files_loc", raw_url=config.get("files_base", None))

    def test_Key(self):
        _key = self.test_schema.Key
        self.assertIsInstance(_key, DatasetKey)
        self.assertEqual(str(_key), "AQUALAB_20260301_to_20260331")

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "AQUALAB")

    def test_base_loc(self):
        _loc = self.test_schema._base_files_location
        self.assertIsInstance(_loc, LocationConfig)
        self.assertEqual(_loc, URLLocationConfig.FromString(name="files_loc", raw_url="https://opengamedata.fielddaylab.wisc.edu/"))

    def test_SessionCount(self):
        _ct = self.test_schema.SessionCount
        self.assertIsInstance(_ct, int)
        self.assertEqual(_ct, 6598)

    def test_PlayerCount(self):
        _ct = self.test_schema.PlayerCount
        self.assertIsNone(_ct)

    def test_OGDVersion(self):
        _ver = self.test_schema.OGDVersion
        self.assertIsNone(_ver)

    def test_OGDRevision(self):
        _ver = self.test_schema.OGDRevision
        self.assertIsInstance(self.test_schema.OGDRevision, str)
        self.assertEqual(self.test_schema.OGDRevision, "6705a6d")

    def test_EventSpecificationVersion(self):
        _ver = self.test_schema.EventSpecificationVersion
        self.assertIsNone(_ver)

    def test_GameEventsFile(self):
        _path = self.test_schema.GameEventsFile()

        url = "https://opengamedata.fielddaylab.wisc.edu/"
        relative = "data/AQUALAB/AQUALAB_20260301_to_20260331_6705a6d_events.zip"
        expected_path = f"{url}{relative}"

        self.assertIsInstance(_path, str)
        self.assertEqual(_path, expected_path)
        with self.subTest(msg="RawEventsFile"):
            _path = self.test_schema.RawEventsFile()
            self.assertIsInstance(_path, str)
            self.assertEqual(_path, expected_path)

    def test_AllEventsFile(self):
        _path = self.test_schema.AllEventsFile()

        url = "https://opengamedata.fielddaylab.wisc.edu/"
        relative = "data/AQUALAB/AQUALAB_20260301_to_20260331_6705a6d_all-events.zip"
        expected_path = f"{url}{relative}"

        self.assertIsInstance(_path, str)
        self.assertEqual(_path, expected_path)
        with self.subTest(msg="EventsFile"):
            _path = self.test_schema.EventsFile()
            self.assertIsInstance(_path, str)
            self.assertEqual(_path, expected_path)

    def test_CombinedFeaturesFile(self):
        _path = self.test_schema.CombinedFeaturesFile()

        self.assertIsNone(_path)
        with self.subTest(msg="FeaturesFile"):
            _path = self.test_schema.FeaturesFile()
            self.assertIsNone(_path)

    def test_SessionsFile(self):
        _path = self.test_schema.SessionsFile()

        url = "https://opengamedata.fielddaylab.wisc.edu/"
        relative = "data/AQUALAB/AQUALAB_20260301_to_20260331_6705a6d_session-features.zip"

        self.assertIsInstance(_path, str)
        self.assertEqual(_path, f"{url}{relative}")

    def test_PlayersFile(self):
        _path = self.test_schema.PlayersFile()

        url = "https://opengamedata.fielddaylab.wisc.edu/"
        relative = "data/AQUALAB/AQUALAB_20260301_to_20260331_6705a6d_player-features.zip"

        self.assertIsInstance(_path, str)
        self.assertEqual(_path, f"{url}{relative}")

    def test_PopulationFile(self):
        _path = self.test_schema.PopulationFile()

        url = "https://opengamedata.fielddaylab.wisc.edu/"
        relative = "data/AQUALAB/AQUALAB_20260301_to_20260331_6705a6d_population-features.zip"

        self.assertIsInstance(_path, str)
        self.assertEqual(_path, f"{url}{relative}")

    def test_NonStandardElements(self):
        _elems = {
            "events_template": "/tree/aqualab",
            "players_template": "/tree/aqualab",
            "population_template": "/tree/aqualab",
            "sessions_template": "/tree/aqualab",
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(set(self.test_schema.NonStandardElements), set(_elems.keys()))
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    def test_NonStandardElementNames(self):
        _elem_names = ["events_template", "players_template", "population_template", "sessions_template"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)
