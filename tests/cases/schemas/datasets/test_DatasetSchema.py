# import libraries
import logging
import unittest
from datetime import date
from pathlib import Path
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from tests.config.t_config import settings

class test_DatasetSchema(TestCase):
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
        cls.test_schema = DatasetSchema(
            name="DatasetSchema", key=DatasetKey(raw_key="GAME_NAME_20250101_to_202050131"),
            game_id="GAME_NAME",
            start_date=date(year=2025, month=1, day=1), end_date=date(year=2025, month=1, day=31), date_modified=date(year=2025, month=2, day=2),
            ogd_revision="123456", filters={}, # TODO : add filters, maybe after this becomes a DatasetFilteringCollection or whatever
            session_ct=100, player_ct=50,
            raw_file=Path("./raw.tsv"),
            events_file=Path("./events.tsv"), events_template=None,
            all_feats_file=Path("./all_feats.tsv"), all_feats_template=None,
            sessions_file=Path("./sessions.tsv"), sessions_template=None,
            players_file=Path("./players.tsv"), players_template=None,
            population_file=Path("./population.tsv"), population_template=None,
            other_elements={"foo":"bar"}
        )

    @staticmethod
    def RunAll():
        pass

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "DatasetSchema")

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

    @unittest.skip("Not Implemented")
    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
               "type" : "List[Dict]",
               "details": {
                  "name":"str",
                  "price":"int"
               },
               "description" : "The buildings available for the player to construct"
        }
        _schema = DatasetSchema.FromDict(name="available_buildings Schema", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "available_buildings Schema")

if __name__ == '__main__':
    unittest.main()
