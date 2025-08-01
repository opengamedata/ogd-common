import logging
import os
import traceback
import zipfile
from pathlib import Path
from typing import Dict, Optional, IO, Set
## import local files
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class CSVConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***
    _VALID_SECONDARY_FILES = [ ExportMode.EVENTS, ExportMode.DETECTORS, ExportMode.FEATURES, ExportMode.SESSION, ExportMode.PLAYER, ExportMode.POPULATION ]
    _SECONDARY_FILE_SUFFIXES = {ExportMode.EVENTS.name:"game-events", ExportMode.DETECTORS:"all-events",
                                ExportMode.FEATURES:"all-features", ExportMode.SESSION.name:"session-features",
                                ExportMode.PLAYER.name:"player-features", ExportMode.POPULATION.name:"population-features"}

    def __init__(self, config:FileStoreConfig, extension:str = ',',
                 with_secondary_files:Set[ExportMode]=set(), with_zipping:bool=False,
                 existing_meta:Optional[Dict]={}):
        # set up data from params
        super().__init__()
        self._config = config
        self._extension = extension
        self._file = None
        self._existing_meta = existing_meta
        self._with_secondary_files = with_secondary_files
        self._secondary_files : Dict[str,Optional[IO]]   = {mode.name:None for mode in CSVConnector._VALID_SECONDARY_FILES}
        self._with_zipping = with_zipping
        self._zip_paths       : Dict[str,Optional[Path]] = {mode.name:None for mode in CSVConnector._VALID_SECONDARY_FILES}

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
            base_file_name : str  = "_".join(self.StoreConfig.Filename.split("_")[:-1])

            for mode in CSVConnector._VALID_SECONDARY_FILES:
                if mode in self._with_secondary_files:
                    suffix = self._SECONDARY_FILE_SUFFIXES[mode.name]
                    file = self.StoreConfig.Folder / f"{base_file_name}_{suffix}.{self._extension}"
                    zip  = self.StoreConfig.Folder / f"{base_file_name}_{suffix}.zip"
                    try:
                        self._secondary_files[mode.name] = open(file, "w+", encoding="utf-8")
                    except FileNotFoundError:
                        Logger.Log(f"Could not find file {file}.", logging.ERROR)
                    else:
                        self._zip_paths[mode.name] = zip

        return ret_val

    def _close(self) -> bool:
        Logger.Log(f"Closing TSV connector...")
        if self.File:
            self.File.close()
            self._closeSecondaryFiles()
            if self._with_zipping:
                self._zipFiles()

        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def RemoveSecondaryFile(self, mode:ExportMode):
        f = self._secondary_files[mode.name]
        if f is not None:
            f.close()

        self._secondary_files[mode.name] = None
        self._with_secondary_files.remove(mode)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _closeSecondaryFiles(self) -> None:
        for mode in self._VALID_SECONDARY_FILES:
            f = self._secondary_files[mode.name]
            if f is not None:
                f.close()

    def _zipFiles(self) -> None:
        # if we have already done this dataset before, rename old zip files
        # (of course, first check if we ever exported this game before).
        if self._existing_meta is not None:
            _existing_game_events_file  = self._existing_meta.get('game_events_file',  self._existing_meta.get('raw_events_file', None))
            # _existing_all_events_file   = self._existing_meta.get('all_events_file',   self._existing_meta.get('events_file', None))
            # _existing_all_feats_file    = self._existing_meta.get('all_features_file', self._existing_meta.get('features_file', None))
            _existing_sess_file    = self._existing_meta.get('sessions_file', None)
            _existing_players_file = self._existing_meta.get('players_file', None)
            _existing_pop_file     = self._existing_meta.get('population_file', None)
            try:
                if _existing_game_events_file is not None and Path(_existing_game_events_file).is_file() and self._zip_paths['game_events'] is not None:
                    Logger.Log(f"Renaming {str(_existing_game_events_file)} -> {self._zip_paths['game_events']}", logging.DEBUG)
                    os.rename(_existing_game_events_file, str(self._zip_paths['game_events']))
                # if _existing_all_events_file is not None and Path(_existing_all_events_file).is_file() and self._zip_paths['all_events'] is not None:
                #     Logger.Log(f"Renaming {str(_existing_all_events_file)} -> {self._zip_paths['all_events']}", logging.DEBUG)
                #     os.rename(_existing_all_events_file, str(self._zip_paths['all_events']))
                if _existing_sess_file is not None and Path(_existing_sess_file).is_file() and self._zip_paths['sessions'] is not None:
                    Logger.Log(f"Renaming {str(_existing_sess_file)} -> {self._zip_paths['sessions']}", logging.DEBUG)
                    os.rename(_existing_sess_file, str(self._zip_paths['sessions']))
                if _existing_players_file is not None and Path(_existing_players_file).is_file() and self._zip_paths['players'] is not None:
                    Logger.Log(f"Renaming {str(_existing_players_file)} -> {self._zip_paths['players']}", logging.DEBUG)
                    os.rename(_existing_players_file, str(self._zip_paths['players']))
                if _existing_pop_file is not None and Path(_existing_pop_file).is_file() and self._zip_paths['population'] is not None:
                    Logger.Log(f"Renaming {str(_existing_pop_file)} -> {self._zip_paths['population']}", logging.DEBUG)
                    os.rename(_existing_pop_file, str(self._zip_paths['population']))
            except FileExistsError as err:
                msg = f"Error while setting up zip files, could not rename an existing file because another file is already using the target name! {err}"
                Logger.Log(msg, logging.ERROR)
            except Exception as err:
                msg = f"Unexpected error while setting up zip files! {type(err)} : {err}"
                Logger.Log(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
        # for each file, try to save out the csv/tsv to a file - if it's one that should be exported, that is.
        for mode in self._VALID_SECONDARY_FILES:
            z_path = self._zip_paths[mode.name]
            if z_path is not None:
                with zipfile.ZipFile(z_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
                    base_file_name : str = "_".join(self.StoreConfig.Filename.split("_")[:-1]) # everything up to suffix
                    dataset_id     : str = "_".join(base_file_name.split("_")[:-1]) # everything up to short hash
                    file_name = f"{base_file_name}_{self._SECONDARY_FILE_SUFFIXES[mode.name]}.{self._extension}"
                    try:
                        self._addToZip(
                            path=self.StoreConfig.Folder / file_name,
                            zip_file=zip_file,
                            path_in_zip=Path(dataset_id) / file_name
                        )
                        self._addToZip(
                            path=self.StoreConfig.Folder / "README.md",
                            zip_file=zip_file,
                            path_in_zip=Path(dataset_id) / "README.md"
                        )
                        zip_file.close()
                        os.remove(self.StoreConfig.Folder / file_name)
                    except FileNotFoundError as err:
                        Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                        traceback.print_tb(err.__traceback__)
        # finally, zip up the primary output file.
        with zipfile.ZipFile(str(self.StoreConfig.Filepath).split(".")[0]+".zip", "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            try:
                self._addToZip(
                    path=self.StoreConfig.Filepath,
                    zip_file=zip_file,
                    path_in_zip=Path(dataset_id) / self.StoreConfig.Filename
                )
                self._addToZip(
                    path=self.StoreConfig.Folder / "README.md",
                    zip_file=zip_file,
                    path_in_zip=Path(dataset_id) / "README.md"
                )
                zip_file.close()
                os.remove(self.StoreConfig.Filepath)
            except FileNotFoundError as err:
                Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                traceback.print_tb(err.__traceback__)

    @staticmethod
    def _addToZip(path, zip_file, path_in_zip) -> None:
        try:
            zip_file.write(path, path_in_zip)
        except FileNotFoundError as err:
            Logger.Log(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)
