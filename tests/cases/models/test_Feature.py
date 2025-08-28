# import libraries
import logging
from pathlib import Path
from unittest import TestCase
from zipfile import ZipFile
# import locals
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.Feature import Feature
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.models.EventSet import EventSet
from tests.config.t_config import settings

class test_Feature(TestCase):
    zipped_file = ZipFile(Path("tests/data/models/BACTERIA_20210201_to_20210202_5c61198_events.zip"))

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="FeatureTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.feature = Feature(
            name="TestFeature",
            feature_type="SomeTypeOfFeature",
            game_unit="*",
            game_unit_index=None,
            app_id="AQUALAB",
            user_id="GreenGiant",
            session_id="20250101012345",
            subfeatures=["Foo"],
            values=["Value", "Bar"]
        )

    @staticmethod
    def RunAll():
        pass

    def test_ColumnNames(self):
        _elems = [
            "name",   "feature_type", "game_unit",  "game_unit_index", 
            "app_id", "user_id",      "session_id", "value"
        ]
        self.assertIsInstance(self.feature.ColumnNames(), list)
        self.assertEqual(self.feature.ColumnNames(), _elems)

    def test_ColumnValues(self):
        _elems = [
            [
                "TestFeature", "SomeTypeOfFeature", "*",              "*", 
                "AQUALAB",     "GreenGiant",        "20250101012345", "Value"
            ],
            [
                "Foo",     "SomeTypeOfFeature", "*",              "*", 
                "AQUALAB", "GreenGiant",        "20250101012345", "Bar"
            ]
        ]
        self.assertIsInstance(self.feature.ColumnValues, list)
        self.assertEqual(self.feature.ColumnValues, _elems)

    def test_ExportMode(self):
        self.assertIsInstance(self.feature.ExportMode, ExportMode)
        self.assertEqual(self.feature.ExportMode, ExportMode.SESSION)

    def test_Name(self):
        self.assertIsInstance(self.feature.Name, str)
        self.assertEqual(self.feature.Name, "TestFeature")

    def test_FeatureType(self):
        self.assertIsInstance(self.feature.FeatureType, str)
        self.assertEqual(self.feature.FeatureType, "SomeTypeOfFeature")

    def test_GameUnit(self):
        self.assertIsInstance(self.feature.GameUnit, str)
        self.assertEqual(self.feature.GameUnit, "*")

    def test_GameUnitIndex(self):
        self.assertIsInstance(self.feature.GameUnitIndex, str)
        self.assertEqual(self.feature.GameUnitIndex, "*")

    def test_Subfeatures(self):
        self.assertIsInstance(self.feature.Subfeatures, list)
        self.assertEqual(self.feature.Subfeatures, ["Foo"])

    def test_FeatureNames(self):
        self.assertIsInstance(self.feature.FeatureNames, list)
        self.assertEqual(self.feature.FeatureNames, ["TestFeature", "Foo"])

    def test_Values(self):
        self.assertIsInstance(self.feature.Values, list)
        self.assertEqual(self.feature.Values, ["Value", "Bar"])

    def test_ValueMap(self):
        self.assertIsInstance(self.feature.ValueMap, dict)
        self.assertEqual(self.feature.ValueMap, {"TestFeature":"Value", "Foo":"Bar"})
