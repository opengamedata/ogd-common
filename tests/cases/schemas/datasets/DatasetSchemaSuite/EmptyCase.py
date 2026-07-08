# import libraries
import logging
import unittest
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

class EmptyCase(TestCase):
    """DatasetSChema test case where no initialization is used at class level.

    Fixture:
    * No initialization of a DatasetSChema object

    Case Categories:
    * Loading functions.
        * Appropriate here since the fixture doesn't set up an object.
    * Parsing functions. 
        * We test these so as to get details of where loading fails.
    """

    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "game_id"            : "GAME_NAME",
            "dataset_id"         : "AQUALAB_20250101_to_20250131",
            "population": {
                "session_count"      : 100,
                "player_count"       : 50,
                "filters"            : {},
            },
            "game_state"         : {},
            "events"             : {},
            "features"           : {},
            "versioning": {
                "ogd_version"        : "1.0.0",
                "ogd_revision"       : "123456",
                "event_spec_version" : "1.0",
            },
            # output info
            "output": {
                # "base_file_location" : str(self._base_files_location),
                "all_events_file"    : "events.tsv",
                "game_events_file"   : "raw.tsv",
                "all_features_file"  : None,
                "sessions_file"      : "sessions.tsv",
                "players_file"       : "players.tsv",
                "population_file"    : "population.tsv"
            },
            # deprecated/compatibility info
            "date_modified"      : "2/2/2025",
            "start_date"         : "1/1/2025",
            "end_date"           : "1/31/2025"
        }
        _schema = DatasetSchema.FromDict(name="EmptyCase Dataset Schema", unparsed_elements=_dict)
        with self.subTest(msg="Name"):
            _str = _schema.Name
            self.assertIsInstance(_str, str)
            self.assertEqual(_str, "EmptyCase Dataset Schema")

        with self.subTest(msg="base_loc"):
            _loc = _schema.BaseFileLocation
            self.assertIsInstance(_loc, LocationConfig)
            self.assertEqual(_loc, DirectoryLocationConfig(name="baseloc", folder_path=Path("data")))

        with self.subTest(msg="SessionCount"):
            _ct = _schema.SessionCount
            self.assertIsInstance(_ct, int)
            self.assertEqual(_ct, 100)

        with self.subTest(msg="PlayerCount"):
            _ct = _schema.PlayerCount
            self.assertIsInstance(_ct, int)
            self.assertEqual(_ct, 50)

        with self.subTest(msg="OGDVersion"):
            _ver = _schema.OGDVersion
            self.assertIsInstance(_ver, SemanticVersion)
            self.assertEqual(_ver, SemanticVersion(1, 0, 0))

        with self.subTest(msg="OGDRevision"):
            _ver = _schema.OGDRevision
            self.assertIsInstance(_ver, str)
            self.assertEqual(_ver, "123456")

        with self.subTest(msg="EventSpecificationVersion"):
            _ver = _schema.EventSpecificationVersion
            self.assertIsInstance(_ver, SemanticVersion)
            self.assertEqual(_ver, SemanticVersion(1, 0))

        base = "data/"
        loc = "raw.tsv"
        for relative in [False, True]:
            path_type = "Relative" if relative else "Absolute"
            expected_path = loc if relative else f"{base}{loc}"
            # Test both relative and absolute paths.
            with self.subTest(rel=relative, msg=f"GameEventsFile: {path_type}"):
                _path = _schema.GameEventsFile(relative=relative)
                self.assertIsInstance(_path, str)
                self.assertEqual(_path, expected_path)
            with self.subTest(rel=False, msg=f"RawEventsFile: {path_type}"):
                _path = _schema.RawEventsFile(relative=relative)
                self.assertIsInstance(_path, str)
                self.assertEqual(_path, expected_path)

        loc = "events.tsv"
        for relative in [False, True]:
            path_type = "Relative" if relative else "Absolute"
            expected_path = loc if relative else f"{base}{loc}"
            # Test both relative and absolute paths.
            with self.subTest(rel=relative, msg=f"AllEventsFile: {path_type}"):
                _path = _schema.AllEventsFile(relative=relative)
                self.assertIsInstance(_path, str)
                self.assertEqual(_path, expected_path)
            with self.subTest(rel=False, msg=f"EventsFile: {path_type}"):
                _path = _schema.EventsFile(relative=relative)
                self.assertIsInstance(_path, str)
                self.assertEqual(_path, expected_path)

        loc = "all_feats.tsv"
        for relative in [False, True]:
            path_type = "Relative" if relative else "Absolute"
            expected_path = loc if relative else f"{base}{loc}"
            # Test both relative and absolute paths.
            with self.subTest(rel=relative, msg=f"CombinedFeaturesFile: {path_type}"):
                _path = _schema.CombinedFeaturesFile(relative=relative)
                self.assertIsNone(_path)
            with self.subTest(rel=False, msg=f"FeaturesFile: {path_type}"):
                _path = _schema.FeaturesFile(relative=relative)
                self.assertIsNone(_path)

        loc = "sessions.tsv"
        for relative in [False, True]:
            expected_path = loc if relative else f"{base}{loc}"
            path_type = "Relative" if relative else "Absolute"
            # Test both relative and absolute paths.
            with self.subTest(rel=relative, msg=f"SessionsFile: {path_type}"):
                _path = _schema.SessionsFile(relative=relative)
                self.assertIsInstance(_path, str)
                self.assertEqual(_path, expected_path)

        loc = "players.tsv"
        for relative in [False, True]:
            expected_path = loc if relative else f"{base}{loc}"
            path_type = "Relative" if relative else "Absolute"
            # Test both relative and absolute paths.
            with self.subTest(rel=relative, msg=f"PlayersFile: {path_type}"):
                _path = _schema.PlayersFile(relative=relative)
                self.assertIsInstance(_path, str)
                self.assertEqual(_path, expected_path)

        loc = "population.tsv"
        for relative in [False, True]:
            expected_path = loc if relative else f"{base}{loc}"
            path_type = "Relative" if relative else "Absolute"
            # Test both relative and absolute paths.
            with self.subTest(rel=relative, msg=f"PopulationFile: {path_type}"):
                _path = _schema.PopulationFile(relative=relative)
                self.assertIsInstance(_path, str)
                self.assertEqual(_path, expected_path)

        with self.subTest(msg="NonStandardElements"):
            # Currently, game_id and dataset_id are not used when parsing.
            # This should probably change, but for the time being, this is the way things are.
            _elems = {}
            self.assertIsInstance(_schema.NonStandardElements, dict)
            self.assertEqual(_schema.NonStandardElements, _elems)

        with self.subTest(msg="NonStandardElementNames"):
            # Currently, game_id and dataset_id are not used when parsing.
            # This should probably change, but for the time being, this is the way things are.
            _elem_names = []
            self.assertIsInstance(_schema.NonStandardElementNames, list)
            self.assertEqual(_schema.NonStandardElementNames, _elem_names)
