import abc
import sys
from typing import Optional, Union
# 3rd-party imports
import pandas as pd
## import local files
from ogd.common.filters import *
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.FileConnector import FileConnector

type PDMask = Union[pd.Series, bool]
class FileInterface(Interface):

    @abc.abstractmethod
    def _read(self) -> pd.DataFrame:
        """Private implementation of the logic to retrieve all data from a file, which then becomes the 'data' the FileInterface returns.

        :return: A pandas dataframe containing all the data from the file.
        :rtype: pd.DataFrame
        """
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:DataTableConfig, fail_fast:bool, connector:Optional[FileConnector]=None):
        self._connector : FileConnector

        super().__init__(config=config, fail_fast=fail_fast)
        self._data : pd.DataFrame
        if connector:
            self._connector = connector
        elif isinstance(self.Config.StoreConfig, FileStoreConfig):
            self._connector = FileConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"CSVInterface config was for a connector other than CSV/TSV files! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open(writeable=False)

    @property
    def DataFrame(self) -> pd.DataFrame:
        return self._data

    @property
    def Extension(self) -> str:
        return self.Connector.FileExtension

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> FileConnector:
        return self._connector

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @classmethod
    def _safeguardFilters(cls, filters:DatasetFilterCollection) -> None:
        """Override of the `_safeguardFilters` function to perform a check on a filter set, and update the filters if they are not satisfactory.

        For FileInterfaces, we are comfortable reading the entirety of a file, so this override simply applies no constraints or defaults, and allows any filtering configuration.

        :param filters: _description_
        :type filters: DatasetFilterCollection
        """
        return

    # *** PRIVATE METHODS ***
