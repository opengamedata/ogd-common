import logging
from pathlib import Path
from typing import Dict, Optional, IO, Set
## import local files
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class CSVConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:FileStoreConfig, extension:str = ',', with_secondary_files:Set[ExportMode]=set()):
        # set up data from params
        super().__init__()
        self._config = config
        self._extension = extension
        self._file = None
        self._with_secondary_files = with_secondary_files
        self._secondary_files     : Dict[str,Optional[IO]]   = {"population":None, "players":None, "sessions":None, "processed_events":None, "raw_events":None}
        self._zip_paths : Dict[str,Optional[Path]] = {"population":None, "players":None, "sessions":None, "processed_events":None, "raw_events":None}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def StoreConfig(self) -> FileStoreConfig:
        return self._config

    @property
    def File(self) -> Optional[IO]:
        return self._file

    @property
    def SecondaryFiles(self) -> Dict[str, Optional[IO]]:
        return self._secondary_files
    @property
    def ZipPaths(self) -> Dict[str, Optional[Path]]:
        return self._zip_paths

    def _open(self) -> bool:
        ret_val = True
        try:
            self._file = open(self.StoreConfig.Filepath, "rw")
        except FileNotFoundError:
            Logger.Log(f"Could not find file {self.StoreConfig.Filepath}.", logging.ERROR)
            ret_val = False
        else:
            game_data_dir : Path = self.StoreConfig.Location.Folder
            base_file_name : str  = "_".join(self.StoreConfig.Location.Filename.split("_")[:-1])

            if ExportMode.EVENTS in self._with_secondary_files:
                file = game_data_dir / f"{base_file_name}_events.{self._extension}"
                zip  = game_data_dir / f"{base_file_name}_events.zip"
                try:
                    self._secondary_files['raw_events'] = open(file, "w+", encoding="utf-8")
                except FileNotFoundError:
                    Logger.Log(f"Could not find file {file}.", logging.ERROR)
                else:
                    self._zip_paths['raw_events'] = zip

            if ExportMode.SESSION in self._with_secondary_files:
                file = game_data_dir / f"{base_file_name}_session-features.{self._extension}"
                zip  = game_data_dir / f"{base_file_name}_session-features.zip"
                try:
                    self._secondary_files['sessions']     = open(f"{file}", "w+", encoding="utf-8")
                except FileNotFoundError:
                    Logger.Log(f"Could not find file {file}.", logging.ERROR)
                else:
                    self._zip_paths['sessions'] = zip

            if ExportMode.PLAYER in self._with_secondary_files:
                file = game_data_dir / f"{base_file_name}_player-features.{self._extension}"
                zip  = game_data_dir / f"{base_file_name}_player-features.zip"
                try:
                    self._secondary_files['players'] = open(file, "w+", encoding="utf-8")
                except FileNotFoundError:
                    Logger.Log(f"Could not find file {file}.", logging.ERROR)
                else:
                    self._zip_paths['players'] = zip

            if ExportMode.POPULATION in self._with_secondary_files:
                file = game_data_dir / f"{base_file_name}_population-features.{self._extension}"
                zip  = game_data_dir / f"{base_file_name}_population-features.zip"
                try:
                    self._secondary_files['population'] = open(file, "w+", encoding="utf-8")
                except FileNotFoundError:
                    Logger.Log(f"Could not find file {file}.", logging.ERROR)
                else:
                    self._zip_paths['population'] = zip

        return ret_val

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
