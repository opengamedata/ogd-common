"""Module for a debugging outerface."""

# import standard libraries
import json
import logging
from typing import Any, Dict, List, Set

# import OGD files
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class DebugOuterface(Outerface):
    """Outerface used for debugging purposes.

    Its destination is standard output; all values are output via print statements.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, export_modes:Set[ExportMode]):
        super().__init__(export_modes=export_modes, config=config)
        # self.Open()

    # *** IMPLEMENT ABSTRACTS ***

    def _removeExportMode(self, mode:ExportMode):
        match mode:
            case ExportMode.EVENTS:
                self._display("No longer outputting raw event data to debug stream.")
            case ExportMode.DETECTORS:
                self._display("No longer outputting processed event data to debug stream.")
            case ExportMode.SESSION:
                self._display("No longer outputting session data to debug stream.")
            case ExportMode.PLAYER:
                self._display("No longer outputting player data to debug stream.")
            case ExportMode.POPULATION:
                self._display("No longer outputting population data to debug stream.")

    def _writeGameEventsHeader(self, header:List[str]) -> None:
        self._display("Raw events header:")
        self._display(header)

    def _writeAllEventsHeader(self, header:List[str]) -> None:
        self._display("Processed events header:")
        self._display(header)

    def _writeSessionHeader(self, header:List[str]) -> None:
        self._display("Sessions header:")
        self._display(header)

    def _writePlayerHeader(self, header:List[str]) -> None:
        self._display("Player header:")
        self._display(header)

    def _writePopulationHeader(self, header:List[str]) -> None:
        self._display("Population header:")
        self._display(header)

    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        self._display("Raw event data:")
        _lengths = [len(elem) for elem in events]
        self._display(f"{len(events)} raw events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        self._display("Processed event data:")
        _lengths = [len(elem) for elem in events]
        self._display(f"{len(events)} processed events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        self._display("Session data:")
        _lengths = [len(elem) for elem in sessions]
        self._display(f"{len(sessions)} events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        self._display("Player data:")
        _lengths = [len(elem) for elem in players]
        self._display(f"{len(players)} events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        self._display("Population data:")
        _lengths = [len(elem) for elem in populations]
        self._display(f"{len(populations)} events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writeMetadata(self, metadata:Dict[str, Any]):
        self._display("Metadata:")
        self._display(json.dumps(metadata))
    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _display(self, msg):
        Logger.Log(f"DebugOuterface: {msg}", logging.DEBUG)
