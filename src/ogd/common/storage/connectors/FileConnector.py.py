import logging
from typing import IO, Optional
from zipfile import ZipFile
## import local files
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class FileConnector(StorageConnector):
    """Base class for connecting to a file.

    The FileConnector and its corresponding interface and outerface handle things like file compression,
    which may apply across different file types for various file-based datasets.
    Subclasses will implement the details of writing to and from specific formats.
    """

    # *** BUILT-INS & PROPERTIES ***

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
        return self.StoreConfig.FileExtension

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, writeable:bool=True) -> bool:
        ret_val = True

        if self.StoreConfig.IsZipped:
            ret_val = self._openZip(writeable=writeable)
        else:
            ret_val = self._openFile(writeable=writeable)

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

    def _openFile(self, writeable:bool) -> bool:
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
