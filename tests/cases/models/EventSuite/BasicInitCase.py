# import libraries
import datetime
import logging
from unittest import TestCase
# import locals
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.models.events.Event import Event, EventSource
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.utils.Logger import Logger
# import locals
from config.t_config import settings

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class BasicInitCase(TestCase):
    """Event model test case where basic initialization is used.
    
    Fixture:
    * Initialize an Event object with hardcoded values for all `__init__(...)` params
    
    Case Categories:
    * Property functions
        * Appropriate for this case, since we are hardcoding initial values and can then test we get them back directly.
    * Converter functions
        * Similar to property functions, this is a good case for checking that "output" functions that convert the data to another format give correct values from all the inputs.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common attributes across the class.

        Since this class currently just tests properties and "output" converter functions, we go ahead and use a single instance of Event shared across the class.
        If any tests are added that have expected side effects, initialization of the instance should be moved to a `setUp(self)` function.
        """
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

    def test_ToRow_OGDMySQLFormat(self):
        """Test the ToRow function using the `OPENGAMEDATA_MYSQL` schema.

        In particular, this schema assumes fields for the IP address and http user agent,
        which are not present in some other input formats. In this case, we expect those elements to be empty.
        """
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
        self.assertIsInstance(_elems, tuple)
        self.assertEqual(_elems, _row)
