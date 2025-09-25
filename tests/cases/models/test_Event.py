# import libraries
import datetime
import logging
from unittest import TestCase
# import locals
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.Event import Event, EventSource
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Version
# import locals
from tests.config.t_config import settings

class test_Event(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="FeatureTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.event = Event(
            app_id="AQUALAB",
            user_id="GreenGiant",
            session_id="1234567890",
            app_version="1.0",
            app_branch="main",
            log_version=3,
            timestamp=datetime.datetime(year=2025, month=1, day=1, hour=10, minute=0, second=0, microsecond=500),
            time_offset=datetime.timezone(datetime.timedelta(hours=2)),
            event_sequence_index=1,
            event_name="session_start",
            event_source=EventSource.GAME,
            event_data={},
            game_state={},
            user_data={}
        )

    @staticmethod
    def RunAll():
        pass

    def test_ColumnNames(self):
        _elems = [
            "session_id",  "app_id",       "timestamp",   "event_name",
            "event_data",  "event_source", "app_version", "app_branch",
            "log_version", "offset",       "user_id",    "user_data",
            "game_state",  "index"
        ]
        self.assertIsInstance(self.event.ColumnNames(), list)
        self.assertEqual(self.event.ColumnNames(), _elems)

    def test_ColumnValues(self):
        _elems = (
            "1234567890", "AQUALAB",   datetime.datetime(year=2025, month=1, day=1, hour=10, minute=0, second=0, microsecond=500), "session_start", 
            {},           "GAME",      "1.0", "main",
            "3",          "UTC+02:00", "GreenGiant", {},
            {},           1
        )
        self.assertIsInstance(self.event.ColumnValues, tuple)
        self.assertEqual(self.event.ColumnValues, _elems)

    def test_AppVersion(self):
        self.assertIsInstance(self.event.AppVersion, str)
        self.assertEqual(self.event.AppVersion, "1.0")

    # TODO : tests for other props

    def test_FromRow_MySQL(self):
        _schema = EventTableSchema.Load(schema_name="OPENGAMEDATA_MYSQL")
        _row = (
            1, "1234567890", "GreenGiant", {}, datetime.datetime(2025, 1, 1, 10, 0, 0),
            500, datetime.timedelta(hours=2),  datetime.datetime(2025, 1, 1, 10, 0, 1),
            "session_start", {}, "GAME", {}, "1.0", "main", 3, 1, "127.0.0.0", "fake user agent"
        )
        _event = Event.FromRow(row=_row, schema=_schema, fallbacks={"app_id":"AQUALAB"})
        _elems = (
            "1234567890",    "AQUALAB",
            datetime.datetime(year=2025, month=1, day=1, hour=10, minute=0, second=0, microsecond=500000),
            "session_start", 
            {"server_time":datetime.datetime(2025, 1, 1, 10, 0, 1)},
            "GAME",          "1.0",        "main",
            "3",             "UTC+02:00",  "GreenGiant",
            {},              {},           1
        )
        self.assertEqual(_event.ColumnValues, _elems)

    def test_ToRow_MySQL(self):
        _schema = EventTableSchema.Load(schema_name="OPENGAMEDATA_MYSQL")
        _row = (
            None,            "1234567890",     "GreenGiant", {},
            datetime.datetime(2025, 1, 1, 10, 0, 0, 500),
            None,
            datetime.timezone(datetime.timedelta(hours=2)),  None,
            "session_start", {},               None,         {},
            "1.0",           "main",           3,            1,
            None,            None
        )
        _elems = self.event.ToRow(schema=_schema)
        self.assertEqual(_elems, _row)
