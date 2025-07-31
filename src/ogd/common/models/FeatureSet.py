## import standard libraries
from typing import Dict, List
# import local files
from ogd.common.filters.collections import *
from ogd.common.filters.Filter import Filter
from ogd.common.models.Feature import Feature

class FeatureSet:
    """Dumb struct that primarily just contains an ordered list of events.
       It also contains information on any filters used to define the dataset, such as a date range or set of versions.
    """

    def __init__(self, features:List[Feature], filters:Dict[str, Filter]) -> None:
        self._features = features
        self._filters = filters

    @property
    def Features(self) -> List[Feature]:
        return self._features

    @property
    def PopulationFeatures(self) -> List[Feature]:
        return [feature for feature in self.Features if feature.PlayerID == "*" and feature.SessionID == "*"]

    @property
    def PlayerFeatures(self) -> List[Feature]:
        return [feature for feature in self.Features if feature.PlayerID != "*"]

    @property
    def SessionFeatures(self) -> List[Feature]:
        return [feature for feature in self.Features if feature.SessionID != "*"]

    @property
    def Filters(self) -> Dict[str, Filter]:
        return self._filters

    @property
    def AsMarkdown(self):
        _filters_clause = "* ".join([f"{key} : {val}" for key,val in self._filters.items()])
        return f"## Feature Dataset\n\n{_filters_clause}"