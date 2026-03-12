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

def setUpModule():
    _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
    _level       = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
    Logger.std_logger.setLevel(_level)

class EmptyCase(TestCase):

    def test_FromRow_OGDMySQLFormat(self):
        """Test the FromRow function using the `OPENGAMEDATA_MYSQL` schema.

        In particular, this schema assumes fields for the IP address and http user agent,
        which are not present in some other input formats.
        """
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