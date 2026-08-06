import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
# 3rd-party imports
import pandas as pd
## import local files
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.locations.FileLocationConfig import FileLocationConfig
from ogd.common.configs.locations.RepositoryLocationConfig import RepositoryLocationConfig
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.storage.IDType import IDType
from ogd.common.storage.VersionType import VersionType
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.interfaces.CSVInterface import CSVInterface
from ogd.common.storage.connectors.DatasetRepositoryConnector import DatasetRepositoryConnector
from ogd.common.utils.Logger import Logger

type PDMask = Union[pd.Series, bool]
class DatasetRepositoryInterface(Interface):

    # *** BUILT-INS & PROPERTIES ***
    def __init__(self, config:DataTableConfig, fail_fast:bool, connector:Optional[DatasetRepositoryConnector]=None):
        super().__init__(config=config, fail_fast=fail_fast)

        self._connector : DatasetRepositoryConnector
        if isinstance(connector, DatasetRepositoryConnector):
            self._connector = connector
        elif isinstance(self.Config.StoreConfig, DatasetRepositoryConfig):
            self._connector = DatasetRepositoryConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"DatasetRepositoryInterface config was for a connector other than dataset repository! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open(writeable=False)

        # After opening our connector, we start setting up the CSV/TSV interfaces
        if isinstance(self.Config.TableLocation, RepositoryLocationConfig):
            loc = self.Config.TableLocation
        else:
            raise TypeError(f"DatasetRepositoryInterface was given a DataTableConfig that does not specify a data table within a repository! It was given a {type(self.Config.TableLocation)} instead!")

        dataset : Optional[DatasetSchema] = self.Connector.GetDatasetSchema(dataset_id=loc.DatasetID, create=False)

        self._all_events    = self._getInterface(file_type="all-events",          path=dataset.AllEventsFile()        if dataset else None, fail_fast=fail_fast)
        self._game_events   = self._getInterface(file_type="game-events",         path=dataset.GameEventsFile()       if dataset else None, fail_fast=fail_fast)
        self._all_feats     = self._getInterface(file_type="combined-features",   path=dataset.CombinedFeaturesFile() if dataset else None, fail_fast=fail_fast)
        self._session_feats = self._getInterface(file_type="session-features",    path=dataset.SessionsFile()         if dataset else None, fail_fast=fail_fast)
        self._player_feats  = self._getInterface(file_type="player-features",     path=dataset.PlayersFile()          if dataset else None, fail_fast=fail_fast)
        self._pop_feats     = self._getInterface(file_type="population-features", path=dataset.PopulationFile()       if dataset else None, fail_fast=fail_fast)

    # @property
    # def Extension(self) -> str:
    #     return self.Connector.FileExtension

    # @property
    # def Delimiter(self) -> str:
    #     match self.Extension:
    #         case "tsv":
    #             return "\t"
    #         case "csv":
    #             return ","
    #         case _:
    #             Logger.Log(f"CSVInterface has unexpected extension {self.Extension}, defaulting to comma-separation!", logging.WARN)
    #             return ","

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> DatasetRepositoryConnector:
        return self._connector

    def _availableIDs(self, id_type:IDType, filters:DatasetFilterCollection) -> List[str]:
        ret_val : List[str] = []

        if self._all_events:
            ret_val = self._all_events.AvailableIDs(id_type=id_type, filters=filters) or ret_val
        elif self._all_feats:
            ret_val = self._all_feats.AvailableIDs(id_type=id_type, filters=filters) or ret_val

        return ret_val

    def _availableDates(self, filters:DatasetFilterCollection) -> Dict[str, datetime]:
        ret_val : Dict[str, datetime] = {}

        if self._all_events:
            ret_val = self._all_events.AvailableDates(filters=filters) or ret_val
        elif self._all_feats:
            ret_val = self._all_feats.AvailableDates(filters=filters) or ret_val

        return ret_val

    def _availableVersions(self, mode:VersionType, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        ret_val : List[SemanticVersion | str] = []

        if self._all_events:
            ret_val = self._all_events.AvailableVersions(mode=mode, filters=filters) or ret_val
        elif self._all_feats:
            ret_val = self._all_feats.AvailableVersions(mode=mode, filters=filters) or ret_val

        return ret_val


    def _getEventRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        ret_val : List[Tuple] = []

        if self._all_events:
            ret_val = self._all_events._getEventRows(filters=filters) or ret_val

        return ret_val

    def _getFeatureRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        """Since CSVInterface just connects to a singular file, the getters for features and events are the same.

        Currently, we just assume you know what kind of dataset you loaded, and are calling the right function.

        :param filters: _description_
        :type filters: DatasetFilterCollection
        :return: _description_
        :rtype: List[Tuple]
        """
        ret_val : List[Tuple] = []

        if self._all_feats:
            ret_val = self._all_feats._getFeatureRows(filters=filters) or ret_val

        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @classmethod
    def _safeguardFilters(cls, filters:DatasetFilterCollection) -> None:
        """Override of the `_safeguardFilters` function to perform a check on a filter set, and update the filters if they are not satisfactory.

        For CSVInterface, we are comfortable reading the entirety of a file, so this override simply applies no constraints or defaults, and allows any filtering configuration.

        :param filters: _description_
        :type filters: DatasetFilterCollection
        """
        return

    # *** PRIVATE METHODS ***

    def _getInterface(self, file_type:str, path:Optional[str], fail_fast:bool) -> Optional[CSVInterface]:
        ret_val : Optional[CSVInterface] = None

        if path:
            cfg_name = f"{self.Config.Name}-{file_type}"
            return CSVInterface(
                config=DataTableConfig(
                    name=cfg_name,
                    store=self.Config.StoreConfig,
                    table_schema=self.Config.TableSchema,
                    table_location=FileLocationConfig.FromPath(name=f"{cfg_name}-location", fullpath=path)
                ),
                fail_fast=fail_fast
            )

        return ret_val

