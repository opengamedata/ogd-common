import logging
from typing import Dict, Optional, IO
## import local files
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class CSVConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:FileStoreConfig,
                 with_zipping:bool=False,
                 existing_meta:Optional[Dict]=None):
        # set up data from params
        super().__init__()
        self._config               : FileStoreConfig          = config
        self._file                 : Optional[IO]             = None
        self._existing_meta        : Dict                     = existing_meta or {}
        self._with_zipping         : bool                     = with_zipping

    # *** PROPERTIES ***

    @property
    def StoreConfig(self) -> FileStoreConfig:
        return self._config

    @property
    def File(self) -> Optional[IO]:
        return self._file

    @property
    def FileExtension(self) -> str:
        candidate_ext = self.StoreConfig.FileExtension
        return candidate_ext if candidate_ext in ["tsv", "csv"] else "tsv"

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, writeable:bool=True) -> bool:
        ret_val = True
        try:
            if self._with_zipping:
                # expect a zip file, and try to open file within zip
                pass
            else:
                # assume we're given a tsv/csv
                self._file = open(self.StoreConfig.Filepath, mode="w+" if writeable else "r", encoding="utf-8")
        except FileNotFoundError:
            Logger.Log(f"Could not find file {self.StoreConfig.Filepath}.", logging.ERROR)
            ret_val = False

        return ret_val

    def _close(self) -> bool:
        Logger.Log("Closing TSV connector...")
        if self.File:
            self.File.close()
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
