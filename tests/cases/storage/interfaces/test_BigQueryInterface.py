# import libraries
import logging
import unittest
from datetime import datetime
from unittest import TestCase
# import 3rd-party libraries
from google.cloud import bigquery
# import ogd libraries.
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.storage.interfaces.BigQueryInterface import BigQueryInterface, ParamaterizedClause
from ogd.common.utils.Logger import Logger
# import locals
from tests.config.t_config import settings

class test_BigQueryInterface(TestCase):
    """Testbed for the GameStoreConfig class.

        TODO : Test more 'enabled' options/combinations.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg : TestConfig = TestConfig.FromDict(name="BQTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        _elems = {
            "DB_TYPE"    : "BIGQUERY",
            "PROJECT_ID" : "wcer-field-day-ogd-1798",
            "PROJECT_KEY": "./tests/config/ogd.json"
        }
        store_config = BigQueryConfig.FromDict(name="OPENGAMEDATA_BQ", unparsed_elements=_elems)

        table_schema = EventTableSchema.FromFile(schema_name="OPENGAMEDATA_BIGQUERY.json", schema_path="./tests/config/")

        _elems = { "source":"OPENGAMEDATA_BQ", "database":"aqualab", "table":"aqualab_daily", "schema":"OPENGAMEDATA_BIGQUERY" }
        config = GameStoreConfig.FromDict(name="BQStoreConfig", unparsed_elements=_elems)
        config.StoreConfig = store_config
        config.Table = table_schema

        cls.test_interface = BigQueryInterface(config=config, fail_fast=True, store=None)

    @staticmethod
    def RunAll():
        pass

    def test_AvailableIDs_sessions(self):
        _start_date = datetime(year=2025, month=7, day=1, hour=0, minute=0, second=0)
        _end_date = datetime(year=2025, month=7, day=1, hour=23, minute=59, second=59)
        _date_filt = SequencingFilterCollection(
            timestamp_filter=RangeFilter(mode=FilterMode.INCLUDE, minimum=_start_date, maximum=_end_date),
            session_index_filter=None
        )
        _ver_filt = VersioningFilterCollection(None, None, None)
        session_ids = self.test_interface.AvailableIDs(mode=IDMode.SESSION, date_filter=_date_filt, version_filter=_ver_filt)
        self.assertIsNotNone(session_ids)
        self.assertIsInstance(session_ids, list)
        if session_ids is not None:
            _actual_ids = {
                "25070113192788822","25063022411352643","25063008581249909","25070108352704598","25070108351726544",
                "25070108592310911","25070109010861117","25070110310263273","25070117315030600","25070110475837490",
                "25070117571249646","25070118022749733","25070118255991070","25070108275657998","25070121351820691",
                "25070121535704606","25070110195891715","25063011022835801","25070110425650275","25062508243129938",
                "25070117222057265","25070117305430697","25070112342813693","25070117393924087","25070119390929852",
                "25070118132297805","25070111545580554","25070111563288705","25070111581675893","25070120253798453",
                "25070116283887067","25070118561988259","25070119002964451","25070119012331269","25070210074112064",
                "25070210203824586","25070122024899628"
            }
            self.assertEqual(set(session_ids), _actual_ids)

    def test_AvailableIDs_users(self):
        _start_date = datetime(year=2025, month=7, day=1, hour=0, minute=0, second=0)
        _end_date = datetime(year=2025, month=7, day=1, hour=23, minute=59, second=59)
        _date_filt = SequencingFilterCollection(
            timestamp_filter=RangeFilter(mode=FilterMode.INCLUDE, minimum=_start_date, maximum=_end_date),
            session_index_filter=None
        )
        _ver_filt = VersioningFilterCollection(None, None, None)
        session_ids = self.test_interface.AvailableIDs(mode=IDMode.USER, date_filter=_date_filt, version_filter=_ver_filt)
        self.assertIsNotNone(session_ids)
        self.assertIsInstance(session_ids, list)
        if session_ids is not None:
            _actual_ids = {
                "MajorAsh","AdjacentShine","SweetJiffy","InfiniteVibe","WinteryGrowth","BurningStyle","SalientFood",
                "SleekBaboon","","LukewarmIntent","OceanicScene","AdequateSkull","VeryCode","HeroicScale","PuzzledBarrel",
                "DozingHonor","AvengingJar","YawningJade","ClashingNews","AlarmingDrive","HandyGator","PartialNote","GleamingHeavy"
            }
            self.assertEqual(set(session_ids), _actual_ids)

    def test_generateWhereClause_ids(self):
        filter_mode = FilterMode.INCLUDE
        id_filter = IDFilterCollection(
            session_filter=SetFilter(mode=filter_mode, set_elements={"1", "2", "3"}),
            player_filter=SetFilter(mode=filter_mode, set_elements={"a", "b", "c"})
        )
        where_clause = self.test_interface._generateWhereClause(
            id_filter=id_filter,
            date_filter=SequencingFilterCollection(None, None),
            version_filter=VersioningFilterCollection(None, None, None),
            event_filter=EventFilterCollection(None, None)
        )

        self.assertIsInstance(where_clause, ParamaterizedClause)
        self.assertEqual(where_clause.clause, "WHERE `session_id`  IN @session_list\nAND `user_id`  IN @user_list")

if __name__ == '__main__':
    unittest.main()
