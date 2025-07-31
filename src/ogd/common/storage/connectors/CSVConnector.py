import logging
from collections import defaultdict
from typing import Optional
# 3rd-party imports
import numpy as np
import pandas as pd
## import local files
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class CSVConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:FileStoreConfig, delim:str = ',', table:Optional[TableSchema]=None):
        # set up data from params
        super().__init__()
        self._config = config
        self._table = table
        self._delimiter = delim
        # set up data from file
        self._data      : pd.DataFrame = pd.DataFrame()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def StoreConfig(self) -> FileStoreConfig:
        return self._config

    @property
    def DataFrame(self) -> pd.DataFrame:
        return self._data

    def _open(self) -> bool:
        try:
            # TODO should include option for access to the TableConfig in the interface, because obviously it should know what form the table takes.
            target_types = defaultdict(str, {
                column.Name : np.dtype(column.ValueType if column.ValueType in {"str", "int", "float"} else "object")
                for column in self._table.Columns
            }) if self._table is not None else None

            date_columns = [
                column.Name for column in self._table.Columns if column.ValueType in {"datetime", "timezone"}
            ] if self._table is not None else []

            self._data = pd.read_csv(
                filepath_or_buffer=self.StoreConfig.Location.Filepath,
                delimiter=self._delimiter,
                dtype=target_types,
                parse_dates=date_columns
            )
            # _data = pd.read_csv(filepath_or_buffer=self._filepath, delimiter=self._delimiter)
            Logger.Log(f"Loaded from CSV, columns are: {self._data.dtypes}", logging.INFO)
            Logger.Log(f"First few rows are:\n{self._data.head(n=3)}")
            # self._data = _data.where(_data.notnull(), None)
            self._is_open = True
            return True
        except FileNotFoundError as err:
            Logger.Log(f"Could not find file {self.StoreConfig.Filepath}.", logging.ERROR)
            return False

    def _close(self) -> bool:
        self._data = pd.DataFrame() # make new dataframe, let old data get garbage collected I assume.
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
