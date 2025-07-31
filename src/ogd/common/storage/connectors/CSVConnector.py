import logging
from typing import Optional, IO
## import local files
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class CSVConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:FileStoreConfig, delim:str = ',', with_secondary_files:bool=False):
        # set up data from params
        super().__init__()
        self._config = config
        self._delimiter = delim
        self._file = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def StoreConfig(self) -> FileStoreConfig:
        return self._config

    @property
    def File(self) -> Optional[IO]:
        return self._file

    def _open(self) -> bool:
        try:
            self._file = open(self.StoreConfig.Filepath, "rw")
        except FileNotFoundError as err:
            Logger.Log(f"Could not find file {self.StoreConfig.Filepath}.", logging.ERROR)
            return False
        else:
            return True

    def _close(self) -> bool:
        if self.File:
            self.File.close()
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
