import json
import logging
import os
import traceback
import zipfile
from pathlib import Path
from typing import Dict, Optional, IO, Set
from urllib import request as urlrequest
from urllib.error import URLError
## import local files
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.configs.storage.RepositoryIndexingConfig import RepositoryIndexingConfig
from ogd.common.models.features.AggregationMode import AggregationMode
from ogd.common.models.features.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.storage.connectors.CSVConnector import CSVConnector
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger
from ogd.common.utils.fileio import loadJSONFile
from ogd.common.utils.typing import Map

class DatasetRepositoryConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***
    _DEFAULT_EXTENSION = "tsv"
    _FILE_SUFFIXES     = {ExportMode.EVENTS.name:"game-events", ExportMode.DETECTORS.name:"all-events",
                          ExportMode.FEATURES.name:"all-features", AggregationMode.SESSION.name:"session-features",
                          AggregationMode.PLAYER.name:"player-features", AggregationMode.POPULATION.name:"population-features"}

    def __init__(self, repository:DatasetRepositoryConfig,
                 extension:Optional[str]=None,
                 with_files:Optional[Set[AggregationMode | ExportMode]]=None,
                 with_zipping:bool=False):
        """Constructor for the DatasetRepositoryConnector

        :param location: The location of the target repository.
        :type location: DirectoryLocationSchema | URLLocationSchema
        :param extension: The file extension type to use, if not set, the class default (tsv) will be used. Defaults to None
        :type extension: Optional[str], optional
        :param with_files: Which file types to use, if not set, defaults to use all file types. Defaults to None
        :type with_files: Optional[Set[ExportMode]], optional
        :param with_zipping: Whether files are zipped or not. If true, any interfaces using this connector will expect files to be inside zips, and outerfaces will zip output files. Defaults to False
        :type with_zipping: bool, optional
        """
        # set up data from params
        super().__init__()
        self._config        : DatasetRepositoryConfig           = repository
        self._extension     : str                               = extension or DatasetRepositoryConnector._DEFAULT_EXTENSION
        self._with_files    : Set[AggregationMode | ExportMode] = with_files or set()
        self._files         : Dict[str,Optional[CSVConnector]]  = {mode:None for mode in AggregationMode.Names() + ExportMode.Names()}
        self._with_zipping  : bool                              = with_zipping
        self._zip_paths     : Dict[str,Optional[Path]]          = {mode:None for mode in AggregationMode.Names() + ExportMode.Names()}
        self._existing_meta : Dict

    # *** PROPERTIES ***

    @property
    def StoreConfig(self) -> DatasetRepositoryConfig:
        return self._config

    @property
    def Files(self) -> Dict[str, Optional[CSVConnector]]:
        return self._files

    @property
    def FileExtension(self) -> str:
        return self._extension

    @property
    def ZipPaths(self) -> Dict[str, Optional[Path]]:
        return self._zip_paths

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, writeable:bool=True) -> bool:
        ret_val = False

        datasets_raw : Map
        try:
            if self.StoreConfig.LocalDirectory is not None:
                datasets_raw = loadJSONFile(filename="file_list.json", path=self.StoreConfig.LocalDirectory.FolderPath)
            elif self.StoreConfig.PublicURL is not None:
                # TODO : figure out the right URL joining to do to get the right file_list.json URL set up
                with urlrequest.urlopen(url=f"{self.StoreConfig.PublicURL.Location}/file_list.json") as remote_datasets_file:
                    datasets_raw = json.loads(remote_datasets_file)
            else:
                datasets_raw = loadJSONFile(filename="file_list.json", path=RepositoryIndexingConfig._DEFAULT_LOCAL_DIR.FolderPath)
        except (ModuleNotFoundError, FileNotFoundError, URLError):
            Logger.Log(f"Could not find dataset information for dataset repository at {self.StoreConfig.Location}", logging.ERROR)
        else:
            self._existing_meta = {
                game_name : DatasetCollectionSchema(name=game_name, datasets=None, other_elements=raw_datasets)
                for game_name, raw_datasets in datasets_raw.items()
            }
            ret_val = True

        # logic for opening files
        for mode in self._with_files:
            suffix = self._FILE_SUFFIXES[mode.name]
            if isinstance(self._location, DirectoryLocationSchema):
                filename = self._location.FolderPath / f"{base_file_name}_{suffix}.{self.FileExtension}"
            _zip  = self.StoreConfig.Folder / f"{base_file_name}_{suffix}.zip"
            try:
                self._files[mode.name] = open(file, "w+", encoding="utf-8")
            except FileNotFoundError:
                Logger.Log(f"Could not find file {file}.", logging.ERROR)
            else:
                self._zip_paths[mode.name] = _zip

        return ret_val

    def _close(self) -> bool:
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def RemoveFile(self, mode:AggregationMode):
        f = self._files[mode.name]
        if f is not None:
            f.close()

        self._files[mode.name] = None
        if mode in self._with_files:
            self._with_files.remove(mode)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _closeSecondaryFiles(self) -> None:
        for mode in self._with_files:
            f = self._files[mode.name]
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
        readme_path = self.StoreConfig.Folder / "README.md"
        for mode in self._VALID_FILES:
            z_path = self._zip_paths[mode.name]
            if z_path is not None:
                with zipfile.ZipFile(z_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            # FIXME : This is dumb, we should have a way to use the DatasetKey. Also, StoreConfig.Filename currently doesn't have the hash included. For features, it at least has _feature at end, though maybe that shouldn't be there yet either...
                    base_file_name : str = "_".join(self.StoreConfig.Filename.split("_")[:-1]) # everything up to suffix
                    dataset_id     : str = "_".join(base_file_name.split("_")[:-1]) # everything up to short hash
                    file_name = f"{base_file_name}_{self._FILE_SUFFIXES[mode.name]}.{self.FileExtension}"
                    try:
                        self._addToZip(
                            path=self.StoreConfig.Folder / file_name,
                            zip_file=zip_file,
                            path_in_zip=Path(dataset_id) / file_name
                        )
                        if readme_path.is_file():
                            self._addToZip(
                                path=self.StoreConfig.Folder / "README.md",
                                zip_file=zip_file,
                                path_in_zip=Path(dataset_id) / "README.md"
                            )
                        else:
                            Logger.Log(f"Missing readme in {self.StoreConfig.Folder}, consider generating readme...", logging.WARNING, depth=1)
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
                if readme_path.is_file():
                    self._addToZip(
                        path=self.StoreConfig.Folder / "README.md",
                        zip_file=zip_file,
                        path_in_zip=Path(dataset_id) / "README.md"
                    )
                else:
                    Logger.Log(f"Missing readme in {self.StoreConfig.Folder}, consider generating readme...", logging.WARNING, depth=1)
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
