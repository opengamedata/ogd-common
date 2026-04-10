# import libraries
import logging
import unittest
from datetime import datetime, timezone
from unittest import TestCase
# import 3rd-party libraries
# from google.cloud import bigquery
# import ogd libraries.
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.configs.storage.MySQLConfig import MySQLConfig
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.storage.IDType import IDType
from ogd.common.filters.FilterMode import FilterMode
from ogd.common.storage.VersionType import VersionType
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.storage.interfaces.MySQLInterface import MySQLInterface
from ogd.common.utils.Logger import Logger
# import locals
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="MySQLTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class OGDMySQLCase(TestCase):
    """Testbed for the BigQueryInterface class.

    TODO : Test more 'enabled' options/combinations.

    Fixture:
    * Open a connection to BQ with basic configuration
    
    Case Categories:
    * Connection management functions
    """

    def setUp(self) -> None:
        """_summary_
        TODO : Check that we're actually setting up in accordance with expectations,
        i.e. that we aren't still using an old approach to setting StoreConfig and TableSchema
        """
        store_config = MySQLConfig.FromDict(
            name="OPENGAMEDATA_MYSQL",
            unparsed_elements=settings.get("MYSQL_TEST_CONFIG", {})
        )
        table_schema = EventTableSchema.FromFile(
            file_name="OPENGAMEDATA_MYSQL.json",
            directory="./src/ogd/common/schemas/tables/presets"
        )
        _elems = { "source":"OPENGAMEDATA_MYSQL", "database":"ogd-reference", "table":"AQUALAB", "schema":"OPENGAMEDATA_MYSQL" }

        config = DataTableConfig.FromDict(name="BQStoreConfig", unparsed_elements=_elems)
        config.StoreConfig = store_config
        config.TableSchema = table_schema

        self.test_interface = MySQLInterface(config=config, fail_fast=True, store=None)

    def test_AvailableIDs_sessions(self):
        # 1. Set up temp vars
        _time_filter = RangeFilter(
            mode=FilterMode.INCLUDE,
            minimum=datetime(year=2026, month=4, day=1, hour=0, minute=0, second=0),
            maximum=datetime(year=2026, month=4, day=8, hour=23, minute=59, second=59)
        )
        _filter_collection = DatasetFilterCollection(
            sequence_filters=SequencingFilterCollection(_time_filter, None),
            version_filters=VersioningFilterCollection(None, None, None)
        )
        _expected_ids = {
            "26033008505741415", "26033100001342145", "26033109323255216", "26033116252063999", "26040107210330116",
            "26040107252910095", "26040108365524465", "26040109183166139", "26040109470471232", "26040110384029996",
            "26040111052502709", "26040112552449753", "26040115140060371", "26040118103124200", "26040118183586780",
            "26040120015944700", "26040120345138333", "26040120493521025", "26040121041863189", "26040208312608236",
            "26040208323679062", "26040208550918549", "26040209272323843", "26040211454725335", "26040211492924518",
            "26040211595710502", "26040212420436015", "26040212511786668", "26040213491076986", "26040215035029831",
            "26040308114291866", "26040308462842696", "26040309134537969", "26040309144888469", "26040310094146395",
            "26040311531409136", "26040316270927195", "26040316422888223", "26040317000812918", "26040317020583184",
            "26040317390515997", "26040318162640480", "26040320444587225", "26040409115411456", "26040411120784392",
            "26040414553828055", "26040415503690905", "26040416335807490", "26040418472841923", "26040420160650030",
            "26040510482137142", "26040515394416140", "26040515514879563", "26040516385109539", "26040609040930890",
            "26040609295689046", "26040609343428380", "26040619190440434", "26040621101662813", "26040704541089596",
            "26040707085637265", "26040708300853919", "26040708564781008", "26040712544174657", "26040717230538152",
            "26040719194589135", "26040721133335666", "26040722553070944"
        }
        # 2. Test stimulus
        session_ids = self.test_interface.AvailableIDs(id_type=IDType.SESSION, filters=_filter_collection)
        # 3. Assertions
        self.assertIsNotNone(session_ids)
        self.assertIsInstance(session_ids, list)
        if session_ids is not None:
            self.assertEqual(set(session_ids), _expected_ids)

    def test_AvailableIDs_users(self):
        # 1. Set up temp vars
        _time_filt = RangeFilter(
            mode=FilterMode.INCLUDE,
            minimum=datetime(year=2026, month=4, day=1, hour=0, minute=0, second=0),
            maximum=datetime(year=2026, month=4, day=8, hour=23, minute=59, second=59))
        _filter_collection = DatasetFilterCollection(
            sequence_filters=SequencingFilterCollection(_time_filt, None),
            version_filters=VersioningFilterCollection(None, None, None)
        )
        _actual_ids = {
            "ConstantVeto", "DamagedBog", "DrySalad",    "EarnestBread",   "ElegantPaper", "ElusiveRuby", "FreshTunic",
            "FunTreaty",    "GameSpeed",  "HardyCure",   "JumbledMorale",  "LateralNoun",  "LockedBasis", "NineViewer",
            "NovelForum",   "NovelTulip", "RebelSafari", "RestoredLoafer", "SuperKoala",   "TimeGoose"
        }
        # 2. Test stimulus
        session_ids = self.test_interface.AvailableIDs(id_type=IDType.USER, filters=_filter_collection)
        # 3. Assertions
        self.assertIsNotNone(session_ids)
        self.assertIsInstance(session_ids, list)
        if session_ids is not None:
            self.assertEqual(set(session_ids), _actual_ids)

    def test_AvailableDates_singleuser(self):
        # 1. Set up temp vars
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"ConstantVeto"})
        )
        # 2. Test stimulus
        dates = self.test_interface.AvailableDates(
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        # 3. Assertions
        self.assertIsNotNone(dates)
        self.assertIsInstance(dates, dict)
        if dates is not None:
            _start_date = datetime(year=2026, month=4, day=2, hour=7, minute=56, second=7, tzinfo=timezone.utc)
            _end_date = datetime(year=2026, month=4, day=7, hour=8, minute=23, second=49, tzinfo=timezone.utc)
            self.assertEqual(dates.get("min"), _start_date)
            self.assertEqual(dates.get("max"), _end_date)

    def test_AvailableVersions_singleuser_log(self):
        # 1. Set up temp vars
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"ConstantVeto"})
        )
        # 2. Test stimulus
        versions = self.test_interface.AvailableVersions(
            mode=VersionType.LOG,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        # 3. Assertions
        self.assertIsNotNone(versions)
        self.assertIsInstance(versions, list)
        if versions is not None:
            self.assertEqual(versions, ["6"])

    def test_AvailableVersions_singleuser_app(self):
        # 1. Set up temp vars
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"ConstantVeto"})
        )
        # 2. Test stimulus
        versions = self.test_interface.AvailableVersions(
            mode=VersionType.APP,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        # 3. Assertions
        self.assertIsNotNone(versions)
        self.assertIsInstance(versions, list)
        if versions is not None:
            self.assertEqual(versions, ["120"])

    def test_AvailableVersions_singleuser_branch(self):
        # 1. Set up temp vars
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"ConstantVeto"})
        )
        # 2. Test stimulus
        branches = self.test_interface.AvailableVersions(
            mode=VersionType.BRANCH,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        # 3. Assertions
        self.assertIsNotNone(branches)
        self.assertIsInstance(branches, list)
        if branches is not None:
            self.assertEqual(branches, ["production"])

    def test_AvailableVersions_multiuser_branch(self):
        # 1. Set up temp vars
        _user_filt = IDFilterCollection(
            player_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements={"ConstantVeto", "DamagedBog"})
        )
        # 2. Test stimulus
        branches = self.test_interface.AvailableVersions(
            mode=VersionType.BRANCH,
            filters=DatasetFilterCollection(id_filters=_user_filt)
        )
        # 3. Assertions
        self.assertIsNotNone(branches)
        self.assertIsInstance(branches, list)
        if branches is not None:
            self.assertEqual(branches, ["production"])

    def test_generateWhereClause_ids(self):
        # 1. Set up temp vars
        set_ints = {"1", "2", "3"}
        set_strs = {"a", "b", "c"}
        id_filter = IDFilterCollection(
            session_filter=SetFilter(mode=FilterMode.INCLUDE, set_elements=set_ints),
            player_filter=SetFilter(mode=FilterMode.EXCLUDE, set_elements=set_strs)
        )
        # 2. Test stimulus
        where_clause = self.test_interface._generateWhereClause(
            filters=DatasetFilterCollection(
                id_filters=id_filter,
                sequence_filters=SequencingFilterCollection(None, None),
                version_filters=VersioningFilterCollection(None, None, None),
                event_filters=EventFilterCollection(None, None)
            )
        )
        # 3. Assertions
        self.assertIsInstance(where_clause, tuple)
        self.assertIsInstance(where_clause[0], str)
        self.assertEqual(where_clause[0], "WHERE `session_id`  IN UNNEST(@session_id_list)\nAND `user_id` NOT IN UNNEST(@user_id_list)")
        self.assertIsInstance(where_clause[1], list)
        self.assertEqual(
            where_clause[1],
            [
                "Foo",
                "Bar"
            ]
        )

    # def test_setFilterClause_include(self):
    #     # 1. Set up temp vars
    #     filter_mode = FilterMode.INCLUDE
    #     set_elems = {"1", "2", "3"}
    #     set_filter=SetFilter(mode=filter_mode, set_elements=set_elems)
    #     # 2. Test stimulus
    #     set_clause = self.test_interface._setFilterClause(
    #         filt=set_filter,
    #         column_name="session_id",
    #         column_type=str
    #     )
    #     # 3. Assertions
    #     self.assertIsInstance(set_clause, ParamaterizedClause)
    #     self.assertIsInstance(set_clause.clause, str)
    #     self.assertEqual(set_clause.clause, "`session_id`  IN UNNEST(@session_id_list)")
    #     self.assertIsInstance(set_clause.params, list)
    #     self.assertEqual(set_clause.params, [bigquery.ArrayQueryParameter(name="session_id_list", array_type="STRING", values=list(set_elems))])

    # def test_setFilterClause_exclude(self):
    #     filter_mode = FilterMode.EXCLUDE
    #     set_elems = {"1", "2", "3"}
    #     set_filter=SetFilter(mode=filter_mode, set_elements=set_elems)
    #     set_clause = self.test_interface._setFilterClause(
    #         filt=set_filter,
    #         column_name="session_id",
    #         column_type=str
    #     )

    #     self.assertIsInstance(set_clause, ParamaterizedClause)
    #     self.assertIsInstance(set_clause.clause, str)
    #     self.assertEqual(set_clause.clause, "`session_id` NOT IN UNNEST(@session_id_list)")
    #     self.assertIsInstance(set_clause.params, list)
    #     self.assertEqual(set_clause.params, [bigquery.ArrayQueryParameter(name="session_id_list", array_type="STRING", values=list(set_elems))])

    # def test_rangeFilterClause_include_str_fullrange(self):
    #     filter_mode = FilterMode.INCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, minimum="1", maximum="5")
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=str
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version`  BETWEEN @log_version_min AND @log_version_max")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(
    #         range_clause.params,
    #         [
    #                 bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value="1"),
    #                 bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value="5")
    #         ]
    #     )

    # def test_rangeFilterClause_include_int_fullrange(self):
    #     filter_mode = FilterMode.INCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, minimum=1, maximum=5)
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=int
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version`  BETWEEN @log_version_min AND @log_version_max")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(
    #         range_clause.params,
    #         [
    #                 bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1),
    #                 bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5)
    #         ]
    #     )

    # def test_rangeFilterClause_include_int_minonly(self):
    #     filter_mode = FilterMode.INCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, minimum=1)
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=int
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version` > @log_version_min")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1) ])

    # def test_rangeFilterClause_include_int_maxonly(self):
    #     filter_mode = FilterMode.INCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, maximum=5)
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=int
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version` < @log_version_max")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5) ])

    # def test_rangeFilterClause_exclude_str_fullrange(self):
    #     filter_mode = FilterMode.EXCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, minimum="1", maximum="5")
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=str
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version` NOT BETWEEN @log_version_min AND @log_version_max")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(
    #         range_clause.params,
    #         [
    #                 bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value="1"),
    #                 bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value="5")
    #         ]
    #     )

    # def test_rangeFilterClause_exclude_int_fullrange(self):
    #     filter_mode = FilterMode.EXCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, minimum=1, maximum=5)
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=int
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version` NOT BETWEEN @log_version_min AND @log_version_max")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(
    #         range_clause.params,
    #         [
    #                 bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1),
    #                 bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5)
    #         ]
    #     )

    # def test_rangeFilterClause_exclude_int_minonly(self):
    #     filter_mode = FilterMode.EXCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, minimum=1)
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=int
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version` < @log_version_min")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_min", type_="INT64", value=1) ])

    # def test_rangeFilterClause_exclude_int_maxonly(self):
    #     filter_mode = FilterMode.EXCLUDE
    #     range_filter=RangeFilter(mode=filter_mode, maximum=5)
    #     range_clause = self.test_interface._rangeFilterClause(
    #         filt=range_filter,
    #         column_name="log_version",
    #         column_type=int
    #     )

    #     self.assertIsInstance(range_clause, ParamaterizedClause)
    #     self.assertIsInstance(range_clause.clause, str)
    #     self.assertEqual(range_clause.clause, "`log_version` > @log_version_max")
    #     self.assertIsInstance(range_clause.params, list)
    #     self.assertEqual(range_clause.params, [ bigquery.ScalarQueryParameter(name="log_version_max", type_="INT64", value=5) ])
