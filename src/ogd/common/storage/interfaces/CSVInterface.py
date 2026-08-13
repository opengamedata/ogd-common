import logging
from collections import defaultdict
from typing import Dict, Optional, Union
# 3rd-party imports
import numpy as np
import pandas as pd
## import local files
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.storage.connectors.FileConnector import FileConnector
from ogd.common.storage.interfaces.FileInterface import FileInterface
from ogd.common.utils.Logger import Logger

type PDMask = Union[pd.Series, bool]
class CSVInterface(FileInterface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:DataTableConfig, fail_fast:bool, connector:Optional[FileConnector]=None):
        super().__init__(config=config, fail_fast=fail_fast, connector=connector)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _read(self) -> pd.DataFrame:
        ret_val : pd.DataFrame

        # TODO should include option for access to the TableConfig in the interface, because obviously it should know what form the table takes.
        _default = lambda : np.dtype("object")
        _mapping : Dict[str, np.dtype] = {
            column.Name : np.dtype(column.ValueType if column.ValueType in {"str", "int", "float"} else "object")
            for column in self.Config.TableSchema.Columns
        }
        target_types = defaultdict(_default, _mapping)

        date_columns = [
            column.Name for column in self.Config.TableSchema.Columns if column.ValueType in {"datetime", "timezone"}
        ] if self.Config.TableSchema is not None else []

        ret_val = pd.read_csv(
            filepath_or_buffer=self.Connector.File,
            delimiter=self.Delimiter,
            dtype=target_types,
            parse_dates=date_columns
        )
        Logger.Log(f"Loaded from CSV, columns are: {self._data.dtypes}", logging.INFO)
        Logger.Log(f"First few rows are:\n{self._data.head(n=3)}")

        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
