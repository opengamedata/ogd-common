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

    def __init__(self, config:FileStoreConfig,
                 with_zipping:bool=False):
        # set up data from params
        super().__init__()
        self._config       : FileStoreConfig   = config
        self._file         : Optional[IO]      = None
        self._with_zipping : bool              = with_zipping
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

        # expect a zip file, and try to open file within zip, based on conventions
        # if it fails, we're fine with erroring out.
        # If file wasn't actually a zip, but a csv/tsv, then fall back on normal behavior.
        if self.StoreConfig.FileExtension == "zip":
            if not self._with_zipping:
                Logger.Log("CSVConnector was given a zip file but not set to open with zipping. Attempting to open from the zip file anyway...", logging.WARNING)
            try:
                self._zip_file = ZipFile(file=self.StoreConfig.Filepath, mode="w" if writeable else "r")
            except FileNotFoundError:
                Logger.Log(f"Could not find file {self.StoreConfig.Filepath}.", logging.ERROR)
                ret_val = False
            else:
                try:
                    inner_path = f"{self.StoreConfig.Filepath.stem.split("_")[:-2]}/{self.StoreConfig.Filepath.stem}.{self.FileExtension}"
                    self._file = self._zip_file.open(name=inner_path)
                except FileNotFoundError:
                    Logger.Log(f"Could not find file {inner_path} within {self.StoreConfig.Filepath}.", logging.ERROR)
                    ret_val = False
        else:
            ret_val = self._openCSV(path=self.StoreConfig.Filepath, writeable=writeable)

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

    def _openCSV(self, path:str | Path, writeable:bool) -> bool:
        ret_val = True

        # assume we're given a tsv/csv, open as normal.
        try:
            self._file = open(path, mode="w+" if writeable else "r", encoding="utf-8")
        except FileNotFoundError:
            Logger.Log(f"Could not find file {path}.", logging.ERROR)
            ret_val = False

        return ret_val