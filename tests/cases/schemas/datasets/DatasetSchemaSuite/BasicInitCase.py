# import libraries
import logging
from datetime import date
from pathlib import Path
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.configs.locations.LocationConfig import LocationConfig
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.configs.locations.FileLocationConfig import FileLocationConfig
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

class BasicInitCase(TestCase):
    """DatasetSchema test case where basic initialization is used.
    
    Fixture:
    * Initialize a DatasetSchema object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions
        * Check that we get back exactly the hardcoded values we passed in to the `__init__(...)` function.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties, we go ahead and use a single instance of `Feature` shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
        cls.test_schema = DatasetSchema(
            name="DatasetSchema", dataset_id=DatasetKey(game_id="GAME_NAME", full_month="01/2025"),
            game_id="GAME_NAME",  session_ct=100, player_ct=50,
            filters={}, # TODO : add filters, maybe after this becomes a DatasetFilteringCollection or whatever
            game_state={}, events={}, features={},
            ogd_version="1.0.0", ogd_revision="123456", event_spec_version="1.0",
            base_files_location=DirectoryLocationConfig(name="baseloc", folder_path=Path("./")),
            game_events_file=FileLocationConfig.FromPath(name="gameevents", fullpath=Path("./raw.tsv")),
            all_events_file=FileLocationConfig.FromPath(name="allevents", fullpath=Path("./events.tsv")),
            combined_feats_file=FileLocationConfig.FromPath(name="combinedfeats", fullpath=Path("./all_feats.tsv")),
            sessions_file=FileLocationConfig.FromPath(name="sessionfeats", fullpath=Path("./sessions.tsv")),
            players_file=FileLocationConfig.FromPath(name="playerfeats", fullpath=Path("./players.tsv")),
            population_file=FileLocationConfig.FromPath(name="populationfeats", fullpath=Path("./population.tsv")),
            start_date=date(year=2025, month=1, day=1), end_date=date(year=2025, month=1, day=31), date_modified=date(year=2025, month=2, day=2),
            other_elements={"foo":"bar"}
        )

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "DatasetSchema")

    def test_base_loc(self):
        _loc = self.test_schema._base_files_location
        self.assertIsInstance(_loc, LocationConfig)
        self.assertEqual(_loc, DirectoryLocationConfig(name="baseloc", folder_path=Path("./")))

    def test_SessionCount(self):
        _ct = self.test_schema.SessionCount
        self.assertIsInstance(_ct, int)
        self.assertEqual(_ct, 100)

    def test_PlayerCount(self):
        _ct = self.test_schema.PlayerCount
        self.assertIsInstance(_ct, int)
        self.assertEqual(_ct, 50)

    def test_OGDVersion(self):
        _ver = self.test_schema.OGDVersion
        self.assertIsInstance(_ver, SemanticVersion)
        self.assertEqual(_ver, SemanticVersion(1, 0, 0))

    def test_OGDRevision(self):
        _ver = self.test_schema.OGDRevision
        self.assertIsInstance(_ver, str)
        self.assertEqual(_ver, "123456")

    def test_EventSpecificationVersion(self):
        _ver = self.test_schema.EventSpecificationVersion
        self.assertIsInstance(_ver, SemanticVersion)
        self.assertEqual(_ver, SemanticVersion(1, 0))

    def test_GameEventsFile(self):
        _path = self.test_schema.GameEventsFile()
        self.assertIsInstance(_path, str)
        self.assertEqual(_path, "./raw.tsv")
        with self.subTest(msg="RawEventsFile"):
            _path = self.test_schema.RawEventsFile()
            self.assertIsInstance(_path, str)
            self.assertEqual(_path, "./raw.tsv")

    def test_AllEventsFile(self):
        _path = self.test_schema.AllEventsFile()
        self.assertIsInstance(_path, str)
        self.assertEqual(_path, "./events.tsv")
        with self.subTest(msg="EventsFile"):
            _path = self.test_schema.EventsFile()
            self.assertIsInstance(_path, str)
            self.assertEqual(_path, "./events.tsv")

    def test_CombinedFeaturesFile(self):
        _path = self.test_schema.CombinedFeaturesFile()
        self.assertIsInstance(_path, str)
        self.assertEqual(_path, "./all_feats.tsv")
        with self.subTest(msg="FeaturesFile"):
            _path = self.test_schema.FeaturesFile()
            self.assertIsInstance(_path, str)
            self.assertEqual(_path, "./all_feats.tsv")

    def test_SessionsFile(self):
        _path = self.test_schema.SessionsFile()
        self.assertIsInstance(_path, str)
        self.assertEqual(_path, "./sessions.tsv")

    def test_PlayersFile(self):
        _path = self.test_schema.PlayersFile()
        self.assertIsInstance(_path, str)
        self.assertEqual(_path, "./players.tsv")

    def test_PopulationFile(self):
        _path = self.test_schema.PopulationFile()
        self.assertIsInstance(_path, str)
        self.assertEqual(_path, "./population.tsv")

    def test_NonStandardElements(self):
        _elems = {
            "foo":"bar"
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    def test_NonStandardElementNames(self):
        _elem_names = ["foo"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)
