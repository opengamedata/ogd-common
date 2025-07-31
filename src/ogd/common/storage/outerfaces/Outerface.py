"""DataOuterface Module
"""
## import standard libraries
import abc
import logging
from typing import Any, Dict, List, Set

# import local files
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.models.GameData import GameData
from ogd.common.models.Event import Event
from ogd.common.models.Feature import Feature
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.typing import ExportRow
from ogd.common.utils.Logger import Logger

class Outerface:
    """Base class for feature and event output.

    :param Interface: _description_
    :type Interface: _type_
    :return: _description_
    :rtype: _type_
    """

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Connector(self) -> StorageConnector:
        pass

    # @abc.abstractmethod
    # def _destination(self, mode:ExportMode) -> str:
    #     pass

    @abc.abstractmethod
    def _removeExportMode(self, mode:ExportMode) -> str:
        pass

    @abc.abstractmethod
    def _writeRawEventsHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writeProcessedEventsHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writeSessionHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writePlayerHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writePopulationHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writeRawEventLines(self, events:List[ExportRow]) -> None:
        pass

    @abc.abstractmethod
    def _writeProcessedEventLines(self, events:List[ExportRow]) -> None:
        pass

    @abc.abstractmethod
    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        pass

    @abc.abstractmethod
    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        pass

    @abc.abstractmethod
    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, export_modes:Set[ExportMode]):
        self._config  : GameStoreConfig = config
        self._modes   : Set[ExportMode] = export_modes
        self._session_ct : int = 0

    @property
    def Config(self) -> GameStoreConfig:
        return self._config

    @property
    def ExportModes(self) -> Set[ExportMode]:
        return self._modes

    @property
    def SessionCount(self) -> int:
        return self._session_ct
    @SessionCount.setter
    def SessionCount(self, new_val) -> None:
        self._session_ct = new_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # def Destination(self, mode:ExportMode):
    #     return self._destination(mode=mode)

    def RemoveExportMode(self, mode:ExportMode):
        self._removeExportMode(mode)
        self._modes.discard(mode)
        Logger.Log(f"Removed mode {mode} from {type(self).__name__} output.", logging.INFO)

    def WriteHeader(self, header:List[str], mode:ExportMode):
        if mode in self.ExportModes:
            match (mode):
                case ExportMode.EVENTS:
                    self._writeRawEventsHeader(header=header)
                    Logger.Log(f"Wrote event header for {self.Config.GameID} events", depth=3)
                case ExportMode.DETECTORS:
                    self._writeProcessedEventsHeader(header=header)
                    Logger.Log(f"Wrote processed event header for {self.Config.GameID} events", depth=3)
                case ExportMode.SESSION:
                    self._writeSessionHeader(header=header)
                    Logger.Log(f"Wrote session feature header for {self.Config.GameID} sessions", depth=3)
                case ExportMode.PLAYER:
                    self._writePlayerHeader(header=header)
                    Logger.Log(f"Wrote player feature header for {self.Config.GameID} players", depth=3)
                case ExportMode.POPULATION:
                    self._writePopulationHeader(header=header)
                    Logger.Log(f"Wrote population feature header for {self.Config.GameID} populations", depth=3)
                case _:
                    Logger.Log(f"Failed to write header for unrecognized export mode {mode}!", level=logging.WARN, depth=3)
        else:
            Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)

    def WriteEvents(self, events:List[Event], mode:ExportMode) -> None:
        if isinstance(self.Config.Table, EventTableSchema):
            lines = [event.ColumnValues for event in events]
            if mode in self.ExportModes:
                match (mode):
                    case ExportMode.EVENTS:
                        self._writeRawEventLines(events=lines)
                        Logger.Log(f"Wrote {len(events)} {self.Config.GameID} events", depth=3)
                    case ExportMode.DETECTORS:
                        self._writeProcessedEventLines(events=lines)
                        Logger.Log(f"Wrote {len(events)} {self.Config.GameID} processed events", depth=3)
                    case _:
                        Logger.Log(f"Failed to write lines for unrecognized Event export mode {mode}!", level=logging.WARN, depth=3)
            else:
                Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)
        else:
            Logger.Log(f"Could not write events from {type(self).__name__}, outerface was not configured for a Events table!", depth=3)

    def WriteFeatures(self, features:List[Feature], mode:ExportMode) -> None:
        if isinstance(self.Config.Table, FeatureTableSchema):
            lines = [feature.ColumnValues for feature in features]
            if mode in self.ExportModes:
                match (mode):
                    case ExportMode.SESSION:
                        self._writeSessionLines(sessions=lines)
                        Logger.Log(f"Wrote {len(features)} {self.Config.GameID} session lines", depth=3)
                    case ExportMode.PLAYER:
                        self._writePlayerLines(players=lines)
                        Logger.Log(f"Wrote {len(features)} {self.Config.GameID} player lines", depth=3)
                    case ExportMode.POPULATION:
                        self._writePopulationLines(populations=lines)
                        Logger.Log(f"Wrote {len(features)} {self.Config.GameID} population lines", depth=3)
                    case _:
                        Logger.Log(f"Failed to write lines for unrecognized Feature export mode {mode}!", level=logging.WARN, depth=3)
            else:
                Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)
        else:
            Logger.Log(f"Could not write features from {type(self).__name__}, outerface was not configured for a Features table!", depth=3)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
