## import standard libraries
from typing import Dict, List
# import local files
from ogd.common.filters.collections import *
from ogd.common.filters.Filter import Filter
from ogd.common.models.Event import Event

class EventDataset:
    """Dumb struct that primarily just contains an ordered list of events.
       It also contains information on any filters used to define the dataset, such as a date range or set of versions.
    """

    def __init__(self, events:List[Event], filters:Dict[str, Filter]) -> None:
        self._events = events
        self._filters = filters

    @property
    def Events(self) -> List[Event]:
        return self._events

    @property
    def Filters(self) -> Dict[str, Filter]:
        return self._filters

    @property
    def AsMarkdown(self):
        _filters_clause = "* ".join([f"{key} : {val}" for key,val in self._filters.items()])
        return f"## Event Dataset\n\n{_filters_clause}"