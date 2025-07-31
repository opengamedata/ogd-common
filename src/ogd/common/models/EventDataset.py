## import standard libraries
from typing import Any, Dict, List
# import local files
from ogd.common.filters.collections import *
from ogd.common.filters.Filter import Filter
from ogd.common.models.Event import Event, EventSource
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema

class EventDataset:
    """Dumb struct that primarily just contains an ordered list of events.
       It also contains information on any filters used to define the dataset, such as a date range or set of versions.
    """

    def __init__(self, events:List[Event], schema:DatasetSchema) -> None:
        self._events = events
        self._schema = schema

    @property
    def Events(self) -> List[Event]:
        return self._events

    @property
    def GameEvents(self) -> List[Event]:
        return [event for event in self.Events if event.EventSource == EventSource.GAME]

    @property
    def Metadata(self) -> DatasetSchema:
        self._schema

    @property
    def Filters(self) -> Dict[str, Filter]:
        return self.Metadata.Filters

    @property
    def SessionCount(self) -> int:
        return self.Metadata.SessionCount

    @property
    def EventsHeader(self) -> List[str]:
        return Event.ColumnNames()

    @property
    def AsMarkdown(self):
        _filters_clause = "* ".join([f"{key} : {val}" for key,val in self._filters.items()])
        return f"## Event Dataset\n\n{_filters_clause}"