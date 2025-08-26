# import libraries
import logging
import unittest
from datetime import datetime, timezone
from unittest import TestCase
# import 3rd-party libraries
from google.cloud import bigquery
# import ogd libraries.
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.storage.interfaces.BigQueryInterface import BigQueryInterface, ParamaterizedClause
from ogd.common.utils.Logger import Logger
# import locals
from tests.config.t_config import settings

class test_BigQueryInterface(TestCase):
    """Testbed for the DataTableConfig class.

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

        _elems = { "source":"OPENGAMEDATA_BQ", "database":"aqualab", "table":"reference", "schema":"OPENGAMEDATA_BIGQUERY" }
        config = DataTableConfig.FromDict(name="BQStoreConfig", unparsed_elements=_elems)
        config.StoreConfig = store_config
        config.TableSchema = table_schema

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
        session_ids = self.test_interface.AvailableIDs(mode=IDMode.SESSION, filters=DatasetFilterCollection(sequence_filters=_date_filt, version_filters=_ver_filt))
        self.assertIsNotNone(session_ids)
        self.assertIsInstance(session_ids, list)
        if session_ids is not None:
            _actual_ids = {
                "25070113192788822", "25070108351726544", "25070109010861117", "25070108592310911", "25070110310263273",
                "25070117315030600", "25070110475837490", "25070118022749733", "25070108275657998", "25070121351820691",
                "25063022411352643", "25070110195891715", "25063011022835801", "25070110425650275", "25062508243129938",
                "25070117222057265", "25070117305430697", "25070112342813693", "25070119390929852", "25070118132297805",
                "25070111545580554", "25070111581675893", "25070116283887067", "25070118255991070", "25063008581249909",
                "25070121535704606", "25070120253798453", "25070117393924087", "25070117571249646", "25070108352704598",
                "25070111563288705"
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
        session_ids = self.test_interface.AvailableIDs(mode=IDMode.USER, filters=DatasetFilterCollection(sequence_filters=_date_filt, version_filters=_ver_filt))
        self.assertIsNotNone(session_ids)
        self.assertIsInstance(session_ids, list)
        if session_ids is not None:
            _actual_ids = {
                "MajorAsh","AdjacentShine","SweetJiffy","InfiniteVibe","WinteryGrowth","BurningStyle","SalientFood",
                "SleekBaboon","","LukewarmIntent","OceanicScene","AdequateSkull","VeryCode","HeroicScale","PuzzledBarrel",
                "DozingHonor","AvengingJar","YawningJade","ClashingNews"
            }
            self.assertEqual(set(session_ids), _actual_ids)

    def test_AvailableDates_singleuser(self):
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"MajorAsh"})
        )
        dates = self.test_interface.AvailableDates(
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        self.assertIsNotNone(dates)
        self.assertIsInstance(dates, dict)
        if dates is not None:
            _start_date = datetime(year=2025, month=7, day=1, hour=5, minute=21, second=8, microsecond=834000, tzinfo=timezone.utc)
            _end_date = datetime(year=2025, month=7, day=2, hour=2, minute=32, second=49, microsecond=167000, tzinfo=timezone.utc)
            self.assertEqual(dates.get("min"), _start_date)
            self.assertEqual(dates.get("max"), _end_date)

    def test_AvailableVersions_singleuser_log(self):
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"MajorAsh"})
        )
        versions = self.test_interface.AvailableVersions(
            mode=VersionType.LOG,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        self.assertIsNotNone(versions)
        self.assertIsInstance(versions, list)
        if versions is not None:
            self.assertEqual(versions, ["5"])

    def test_AvailableVersions_singleuser_app(self):
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"MajorAsh"})
        )
        versions = self.test_interface.AvailableVersions(
            mode=VersionType.APP,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        self.assertIsNotNone(versions)
        self.assertIsInstance(versions, list)
        if versions is not None:
            self.assertEqual(versions, ["110"])

    def test_AvailableVersions_singleuser_branch(self):
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"MajorAsh"})
        )
        branches = self.test_interface.AvailableVersions(
            mode=VersionType.BRANCH,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        self.assertIsNotNone(branches)
        self.assertIsInstance(branches, list)
        if branches is not None:
            self.assertEqual(branches, ["production-no-failure-prediction-original-job-graph"])

    def test_AvailableVersions_multiuser_branch(self):
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"MajorAsh", "InfiniteVibe"})
        )
        branches = self.test_interface.AvailableVersions(
            mode=VersionType.BRANCH,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        self.assertIsNotNone(branches)
        self.assertIsInstance(branches, list)
        if branches is not None:
            _expected_branches = {
                "production-no-failure-prediction-original-job-graph",
                "production-no-failure-prediction-alt-job-graph"
            }
            self.assertEqual(set(branches), _expected_branches)

    def test_generateWhereClause_ids(self):
        set_ints = {"1", "2", "3"}
        set_strs = {"a", "b", "c"}
        id_filter = IDFilterCollection(
            session_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements=set_ints),
            player_filter=SetFilter(mode=FilterMode.EXCLUDE, set_elements=set_strs)
        )
        where_clause = self.test_interface._generateWhereClause(
            filters=DatasetFilterCollection(
                id_filters=id_filter,
                sequence_filters=SequencingFilterCollection(None, None),
                version_filters=VersioningFilterCollection(None, None, None),
                event_filters=EventFilterCollection(None, None)
            )
        )

        self.assertIsInstance(where_clause, ParamaterizedClause)
        self.assertIsInstance(where_clause.clause, str)
        self.assertEqual(where_clause.clause, "WHERE `session_id`  IN UNNEST(@session_id_list)\nAND `user_id` NOT IN UNNEST(@user_id_list)")
        self.assertIsInstance(where_clause.params, list)
        self.assertEqual(
            where_clause.params,
            [
                bigquery.ArrayQueryParameter(name="session_id_list", array_type="STRING", values=list(set_ints)),
                bigquery.ArrayQueryParameter(name="user_id_list", array_type="STRING", values=list(set_strs))
            ]
        )

    def test_setFilterClause_include(self):
        filter_mode = FilterMode.INCLUDE
        set_elems = {"1", "2", "3"}
        set_filter=SetFilter(mode=filter_mode, set_elements=set_elems)
        set_clause = self.test_interface._setFilterClause(
            filt=set_filter,
            column_name="session_id",
            column_type=str
        )

        self.assertIsInstance(set_clause, ParamaterizedClause)
        self.assertIsInstance(set_clause.clause, str)
        self.assertEqual(set_clause.clause, "`session_id`  IN UNNEST(@session_id_list)")
        self.assertIsInstance(set_clause.params, list)
        self.assertEqual(set_clause.params, [bigquery.ArrayQueryParameter(name="session_id_list", array_type="STRING", values=list(set_elems))])

    def test_setFilterClause_exclude(self):
        filter_mode = FilterMode.EXCLUDE
        set_elems = {"1", "2", "3"}
        set_filter=SetFilter(mode=filter_mode, set_elements=set_elems)
        set_clause = self.test_interface._setFilterClause(
            filt=set_filter,
            column_name="session_id",
            column_type=str
        )

        self.assertIsInstance(set_clause, ParamaterizedClause)
        self.assertIsInstance(set_clause.clause, str)
        self.assertEqual(set_clause.clause, "`session_id` NOT IN UNNEST(@session_id_list)")
        self.assertIsInstance(set_clause.params, list)
        self.assertEqual(set_clause.params, [bigquery.ArrayQueryParameter(name="session_id_list", array_type="STRING", values=list(set_elems))])

    def test_rangeFilterClause_include_str_fullrange(self):
        filter_mode = FilterMode.INCLUDE
        range_filter=RangeFilter(mode=filter_mode, minimum="1", maximum="5")
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=str
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version`  BETWEEN @log_version_min AND @log_version_max")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(
            range_clause.params,
            [
                    bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value="1"),
                    bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value="5")
            ]
        )

    def test_rangeFilterClause_include_int_fullrange(self):
        filter_mode = FilterMode.INCLUDE
        range_filter=RangeFilter(mode=filter_mode, minimum=1, maximum=5)
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=int
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version`  BETWEEN @log_version_min AND @log_version_max")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(
            range_clause.params,
            [
                    bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1),
                    bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5)
            ]
        )

    def test_rangeFilterClause_include_int_minonly(self):
        filter_mode = FilterMode.INCLUDE
        range_filter=RangeFilter(mode=filter_mode, minimum=1)
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=int
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version` > @log_version_min")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1) ])

    def test_rangeFilterClause_include_int_maxonly(self):
        filter_mode = FilterMode.INCLUDE
        range_filter=RangeFilter(mode=filter_mode, maximum=5)
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=int
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version` < @log_version_max")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5) ])

    def test_rangeFilterClause_exclude_str_fullrange(self):
        filter_mode = FilterMode.EXCLUDE
        range_filter=RangeFilter(mode=filter_mode, minimum="1", maximum="5")
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=str
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version` NOT BETWEEN @log_version_min AND @log_version_max")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(
            range_clause.params,
            [
                    bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value="1"),
                    bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value="5")
            ]
        )

    def test_rangeFilterClause_exclude_int_fullrange(self):
        filter_mode = FilterMode.EXCLUDE
        range_filter=RangeFilter(mode=filter_mode, minimum=1, maximum=5)
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=int
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version` NOT BETWEEN @log_version_min AND @log_version_max")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(
            range_clause.params,
            [
                    bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1),
                    bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5)
            ]
        )

    def test_rangeFilterClause_exclude_int_minonly(self):
        filter_mode = FilterMode.EXCLUDE
        range_filter=RangeFilter(mode=filter_mode, minimum=1)
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=int
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version` < @log_version_min")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1) ])

    def test_rangeFilterClause_exclude_int_maxonly(self):
        filter_mode = FilterMode.EXCLUDE
        range_filter=RangeFilter(mode=filter_mode, maximum=5)
        range_clause = self.test_interface._rangeFilterClause(
            filt=range_filter,
            column_name="log_version",
            column_type=int
        )

        self.assertIsInstance(range_clause, ParamaterizedClause)
        self.assertIsInstance(range_clause.clause, str)
        self.assertEqual(range_clause.clause, "`log_version` > @log_version_max")
        self.assertIsInstance(range_clause.params, list)
        self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5) ])

if __name__ == '__main__':
    unittest.main()
