import logging
from pathlib import Path
from typing import Final, IO, Optional, Set
from zipfile import ZipFile
## import local files
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class CSVConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***
    _DEFAULT_EXTENSION : Final[str]      = "tsv"
    _VALID_EXTENSIONS  : Final[Set[str]] = {"tsv", "csv"}

    def __init__(self, config:FileStoreConfig):
        # set up data from params
        super().__init__()
        self._config       : FileStoreConfig   = config
        self._file         : Optional[IO]      = None
        self._zip_file     : Optional[ZipFile] = None

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
        return candidate_ext if candidate_ext in CSVConnector._VALID_EXTENSIONS else CSVConnector._DEFAULT_EXTENSION

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, writeable:bool=True) -> bool:
        ret_val = True

        if self.StoreConfig.IsZipped:
            ret_val = self._openZip(writeable=writeable)
        elif self.StoreConfig.FileExtension in CSVConnector._VALID_EXTENSIONS:
            ret_val = self._openCSV(writeable=writeable)
        else:
            msg = f"Can not open CSVConnector for configured file {self.StoreConfig.Filename}, it has invalid extension {self.StoreConfig.FileExtension}!"
            Logger.Log(message=msg, level=logging.WARN)

        return ret_val

    def _close(self) -> bool:
        Logger.Log("Closing TSV connector...")
        if self.File:
            self.File.close()
        if self._zip_file:
            self._zip_file.close()
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _openCSV(self, writeable:bool) -> bool:
        ret_val = True

        path = self.StoreConfig.Filepath
        # assume we're given a tsv/csv, open as normal.
        try:
            self._file = open(path, mode="w+" if writeable else "r", encoding="utf-8")
        except FileNotFoundError:
            Logger.Log(f"Could not find file {path}.", logging.ERROR)
            ret_val = False

        return ret_val

    def _openZip(self, writeable:bool) -> bool:
        ret_val = True

        zip_path = self.StoreConfig.Filepath
        try:
            self._zip_file = ZipFile(file=zip_path, mode="w" if writeable else "r")
        except FileNotFoundError:
            Logger.Log(f"Could not find file {zip_path}.", logging.ERROR)
            ret_val = False
        else:
            try:
                # if we're going to the trouble of digging in for a zipped file, we'll assume OGD conventions.
                # by OGD convention, we expect format of GAMEID_YYYYMMDD_to_YYYYMMDD_hash_data-type.zip as the zip's file name.
                # TODO : Make use of the Dataset ID model to handle this.
                dataset_id = zip_path.stem.split("_")[:-2]
                inner_path = f"{dataset_id}/{zip_path.stem}.{self.FileExtension}"
                self._file = self._zip_file.open(name=inner_path)
            except FileNotFoundError:
                Logger.Log(f"Could not find file {inner_path} within {self.StoreConfig.Filepath}.", logging.ERROR)
                ret_val = False

        return ret_val
