## import standard libraries
import logging
import sys
from typing import Any, List, Optional, override, Set, Tuple
# 3rd-party imports
# import local files
# from ogd import games
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.models.features.AggregationMode import AggregationMode
from ogd.common.models.features.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.storage.connectors.CSVConnector import CSVConnector
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class CSVOuterface(Outerface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, table_config:DataTableConfig, export_modes:Set[ExportMode | AggregationMode], store:Optional[CSVConnector]=None):
        self._store : CSVConnector

        super().__init__(table_config=table_config, export_modes=export_modes)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, FileStoreConfig):
            self._store = CSVConnector(
                config=self.Config.StoreConfig,
            )
        else:
            raise ValueError(f"CSVInterface config was for a connector other than CSV/TSV files! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

    @property
    def Connector(self) -> CSVConnector:
        return self._store

    @property
    def FileExtension(self) -> str:
        return self.Connector.FileExtension

    @property
    def Delimiter(self) -> str:
        match self.FileExtension:
            case "tsv":
                return "\t"
            case "csv":
                return ","
            case _:
                Logger.Log(f"CSVOuterface has unexpected extension {self.FileExtension}, defaulting to comma-separation!", logging.WARN)
                return ","

    # *** IMPLEMENT ABSTRACTS ***

    @override
    def _removeExportMode(self, mode:ExportMode):
        pass

    @override
    def _setupGameEventsTable(self, header:List[str]) -> None:
        cols = CSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        if self.Connector.File is not None:
            self.Connector.File.writelines(cols_line)
        else:
            Logger.Log(f"No {self.FileExtension} file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    @override
    def _setupDetectorEventsTable(self, header:List[str]) -> None:
        """Since CSVInterface is meant to hold just one type of data, setups are all the same.

        :param header: _description_
        :type header: List[str]
        """
        self._setupGameEventsTable(header=header)

    @override
    def _setupAllFeaturesTable(self, header:List[str]) -> None:
        """Since CSVInterface is meant to hold just one type of data, setups are all the same.

        :param header: _description_
        :type header: List[str]
        """
        self._setupGameEventsTable(header=header)

    @override
    def _setupSessionTable(self, header:List[str]) -> None:
        """Since CSVInterface is meant to hold just one type of data, setups are all the same.

        :param header: _description_
        :type header: List[str]
        """
        self._setupGameEventsTable(header=header)

    @override
    def _setupPlayerTable(self, header:List[str]) -> None:
        """Since CSVInterface is meant to hold just one type of data, setups are all the same.

        :param header: _description_
        :type header: List[str]
        """
        self._setupGameEventsTable(header=header)

    @override
    def _setupPopulationTable(self, header:List[str]) -> None:
        """Since CSVInterface is meant to hold just one type of data, setups are all the same.

        :param header: _description_
        :type header: List[str]
        """
        self._setupGameEventsTable(header=header)

    @override
    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        event_strs = [CSVOuterface._cleanSpecialChars(vals=[str(item) for item in event]) for event in events]
        event_lines = ["\t".join(event) + "\n" for event in event_strs]
        if self.Connector.File is not None:
            self.Connector.File.writelines(event_lines)
        else:
            Logger.Log("No raw_events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(event_lines))

    @override
    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        """Since CSVInterface is meant to hold just one type of data, writes are all the same.

        :param events: _description_
        :type events: List[ExportRow]
        """
        self._writeGameEventLines(events=events)

    @override
    def _writeAllFeatureLines(self, feature_lines:List[ExportRow]) -> None:
        """Since CSVInterface is meant to hold just one type of data, writes are all the same.

        :param events: _description_
        :type events: List[ExportRow]
        """
        self._writeGameEventLines(events=feature_lines)

    @override
    def _writeSessionLines(self, session_lines:List[ExportRow]) -> None:
        """Since CSVInterface is meant to hold just one type of data, writes are all the same.

        :param events: _description_
        :type events: List[ExportRow]
        """
        self._writeGameEventLines(events=session_lines)

    @override
    def _writePlayerLines(self, player_lines:List[ExportRow]) -> None:
        """Since CSVInterface is meant to hold just one type of data, writes are all the same.

        :param events: _description_
        :type events: List[ExportRow]
        """
        self._writeGameEventLines(events=player_lines)

    @override
    def _writePopulationLines(self, population_lines:List[ExportRow]) -> None:
        """Since CSVInterface is meant to hold just one type of data, writes are all the same.

        :param events: _description_
        :type events: List[ExportRow]
        """
        self._writeGameEventLines(events=population_lines)

    @override
    def _writeMetadata(self, dataset_schema:DatasetSchema):
        return

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _cleanSpecialChars(vals:List[Any] | Tuple[Any], tab_width:int=3) -> Tuple[str,...]:
        ret_val : List[str] = [""]*len(vals)
        # check all return values for strings, and ensure no newlines or tabs get through, as they could throw off our outputs.
        for i,val in enumerate(vals):
            ret_val[i] = str(val).replace('\n', ' ').replace('\t', ' '*tab_width)
        return tuple(ret_val)

    # *** PRIVATE METHODS ***
