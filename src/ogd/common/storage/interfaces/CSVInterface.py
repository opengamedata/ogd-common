import logging
import pandas as pd
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
# 3rd-party imports
import numpy as np
import pandas as pd
## import local files
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.CSVConnector import CSVConnector
from ogd.common.utils.Logger import Logger

type PDMask = Union[pd.Series, bool]
class CSVInterface(Interface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, fail_fast:bool, extension:str="tsv", store:Optional[CSVConnector]=None):
        self._store : CSVConnector

        super().__init__(config=config, fail_fast=fail_fast)
        self._extension = extension
        self._data = pd.DataFrame()
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, FileStoreConfig):
            self._store = CSVConnector(config=self.Config.StoreConfig, extension=self._extension, with_secondary_files=set())
        else:
            raise ValueError(f"CSVInterface config was for a connector other than CSV/TSV files! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

        # We always just read the file right away.
        if self.Connector.IsOpen and self.Connector.File:
            # TODO should include option for access to the TableConfig in the interface, because obviously it should know what form the table takes.
            target_types = defaultdict(str, {
                column.Name : np.dtype(column.ValueType if column.ValueType in {"str", "int", "float"} else "object")
                for column in self.Config.Table.Columns
            }) if self.Config.Table is not None else None

            date_columns = [
                column.Name for column in self.Config.Table.Columns if column.ValueType in {"datetime", "timezone"}
            ] if self.Config.Table is not None else []

            self._data = pd.read_csv(
                filepath_or_buffer=self.Connector.File,
                delimiter=self.Delimiter,
                dtype=target_types,
                parse_dates=date_columns
            )
            Logger.Log(f"Loaded from CSV, columns are: {self._data.dtypes}", logging.INFO)
            Logger.Log(f"First few rows are:\n{self._data.head(n=3)}")

    @property
    def DataFrame(self) -> pd.DataFrame:
        return self._data

    @property
    def Extension(self) -> str:
        return self._extension

    @property
    def Delimiter(self) -> str:
        match self.Extension:
            case "tsv":
                return "\t"
            case "csv":
                return ","
            case _:
                Logger.Log(f"CSVInterface has unexpected extension {self.Extension}, defaulting to comma-separation!", logging.WARN)
                return ","

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> CSVConnector:
        return self._store

    def _availableIDs(self, mode:IDMode, date_filter:SequencingFilterCollection, version_filter:VersioningFilterCollection) -> List[str]:
        ret_val : List[str] = []

        if not self.DataFrame.empty:
            server_times = pd.to_datetime(self.DataFrame['server_time'])
            mask = None
            if date_filter.TimestampFilter:
                if date_filter.TimestampFilter.Min and date_filter.TimestampFilter.Max:
                    mask = (server_times >= date_filter.TimestampFilter.Min) & (server_times <= date_filter.TimestampFilter.Max)
                if date_filter.TimestampFilter.Min:
                    mask = server_times >= date_filter.TimestampFilter.Min
                if date_filter.TimestampFilter.Min and date_filter.TimestampFilter.Max:
                    mask = server_times <= date_filter.TimestampFilter.Max
            # if versions is not None and versions is not []:
            #     mask = mask & (self._data['app_version'].isin(versions))
            data_masked = self.DataFrame.loc[mask] if mask is not None else self.DataFrame
            ret_val = [str(id) for id in data_masked['session_id'].unique().tolist()]

        return ret_val

    def _availableDates(self, id_filter:IDFilterCollection, version_filter:VersioningFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str,datetime] = {}

        if self.Connector.IsOpen:
            sess_mask : PDMask = True
            if id_filter.SessionFilter:
                match id_filter.SessionFilter.FilterMode:
                    case FilterMode.INCLUDE:
                        sess_mask = self.DataFrame['session_id'].isin(id_filter.SessionFilter.AsSet)
                    case FilterMode.EXCLUDE:
                        sess_mask = ~self.DataFrame['session_id'].isin(id_filter.SessionFilter.AsSet)
            user_mask : PDMask = True
            if id_filter.PlayerFilter:
                match id_filter.PlayerFilter.FilterMode:
                    case FilterMode.INCLUDE:
                        user_mask = self.DataFrame['user_id'].isin(id_filter.PlayerFilter.AsSet)
                    case FilterMode.EXCLUDE:
                        user_mask = ~self.DataFrame['user_id'].isin(id_filter.PlayerFilter.AsSet)

            _col  = self.DataFrame[sess_mask & user_mask]['timestamp']
            min_date = _col.min()
            max_date = _col.max()
            ret_val = {'min':pd.to_datetime(min_date), 'max':pd.to_datetime(max_date)}

        return ret_val

    def _availableVersions(self, mode:VersionType, id_filter:IDFilterCollection, date_filter:SequencingFilterCollection) -> List[SemanticVersion | str]:
        ret_val : List[SemanticVersion | str] = []

        if self.Connector.IsOpen:
            version_col  : str = "log_version" if mode==VersionType.LOG else "app_version" if mode==VersionType.APP else "app_branch"
            ret_val = [SemanticVersion.FromString(str(ver)) for ver in self.DataFrame[version_col].unique().tolist()]

        return ret_val


    def _getEventRows(self, id_filter:IDFilterCollection, date_filter:SequencingFilterCollection, version_filter:VersioningFilterCollection, event_filter:EventFilterCollection) -> List[Tuple]:
        ret_val : List[Tuple] = []

        if self.Connector.IsOpen and not self.DataFrame.empty:
            sess_mask : PDMask = True
            if id_filter.SessionFilter:
                match id_filter.SessionFilter.FilterMode:
                    case FilterMode.INCLUDE:
                        sess_mask = self.DataFrame['session_id'].isin(id_filter.SessionFilter.AsSet)
                    case FilterMode.EXCLUDE:
                        sess_mask = ~self.DataFrame['session_id'].isin(id_filter.SessionFilter.AsSet)
            user_mask : PDMask = True
            if id_filter.PlayerFilter:
                match id_filter.PlayerFilter.FilterMode:
                    case FilterMode.INCLUDE:
                        user_mask = self.DataFrame['user_id'].isin(id_filter.PlayerFilter.AsSet)
                    case FilterMode.EXCLUDE:
                        user_mask = ~self.DataFrame['user_id'].isin(id_filter.PlayerFilter.AsSet)
            event_mask : PDMask = True
            if event_filter.EventNameFilter:
                match event_filter.EventNameFilter.FilterMode:
                    case FilterMode.INCLUDE:
                        event_mask = self.DataFrame['event_name'].isin(event_filter.EventNameFilter.AsSet)
                    case FilterMode.EXCLUDE:
                        event_mask = ~self.DataFrame['event_name'].isin(event_filter.EventNameFilter.AsSet)
            _data = self.DataFrame[sess_mask & user_mask & event_mask]
            ret_val = list(_data.itertuples(index=False, name=None))
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
