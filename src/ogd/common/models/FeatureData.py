from typing import Any, List, Optional

from ogd.common.models.GameData import GameData
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class FeatureData(GameData):
    def __init__(self, name:str,            feature_type:str,         count_index:Optional[int],
                 cols:List[str],            vals:List[Any],           mode:ExtractionMode,
                 app_id:str,                user_id:Optional[str],    session_id:str,
                 app_version:Optional[str], app_branch:Optional[str], log_version:Optional[str]):
        super().__init__(app_id=app_id,           user_id=user_id,       session_id=session_id,
                         app_version=app_version, app_branch=app_branch, log_version=log_version)
        self._name = name
        self._feature_type = feature_type
        self._count_index = count_index
        self._cols = cols
        self._vals = vals
        self._mode = mode

    def __str__(self) -> str:
        return f"Name: {self.Name}\tCount Index: {self.CountIndex}\nColumns: {self._cols}\t Values: {self._vals}\nMode: {self._mode.name}\tPlayer: {self.PlayerID}\tSession: {self.SessionID}"

    def __repr__(self) -> str:
        return self.Name

    @property
    def Name(self):
        return self._name

    @property
    def FeatureType(self):
        return self._feature_type

    @property
    def CountIndex(self):
        return self._count_index

    @property
    def FeatureNames(self) -> List[str]:
        return self._cols

    @property
    def FeatureValues(self) -> List[Any]:
        return self._vals

    @property
    def ExportMode(self):
        return self._mode
