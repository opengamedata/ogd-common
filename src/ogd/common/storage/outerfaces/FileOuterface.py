## import standard libraries
import logging
import sys
from enum import StrEnum
from typing import Any, List, Optional, override, Set, Tuple
# 3rd-party imports
# import local files
# from ogd import games
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.models.features.AggregationMode import AggregationMode
from ogd.common.models.features.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.storage.connectors.FileConnector import FileConnector
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class FileOuterface(Outerface):
    class ValidExtensions(StrEnum):
        TSV = "tsv"
        CSV = "csv"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, table_config:DataTableConfig, export_modes:Set[ExportMode | AggregationMode], store:Optional[FileConnector]=None):
        self._store : FileConnector

        super().__init__(table_config=table_config, export_modes=export_modes)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, FileStoreConfig):
            self._store = FileConnector(
                config=self.Config.StoreConfig,
            )
        else:
            raise ValueError(f"{self.__class__.__name__} config was for a connector other than files! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

    @property
    def Extension(self) -> str:
        return self.Connector.FileExtension

    # *** IMPLEMENT ABSTRACTS ***

    @property
    def Connector(self) -> FileConnector:
        return self._store

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
