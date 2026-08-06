## import standard libraries
import json
import logging
import os
import re
import shutil
import sys
from git.repo import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from pathlib import Path
from typing import Any, List, Optional, override, Set, Tuple
# 3rd-party imports
# import local files
# from ogd import games
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.locations.RepositoryLocationConfig import RepositoryLocationConfig
from ogd.common.configs.locations.FileLocationConfig import FileLocationConfig
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.models.features.AggregationMode import AggregationMode
from ogd.common.models.features.ExportMode import ExportMode
from ogd.common.models.events.EventSet import EventSet
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.storage.connectors.DatasetRepositoryConnector import DatasetRepositoryConnector
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.storage.outerfaces.CSVOuterface import CSVOuterface
from ogd.common.utils import fileio
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class DatasetRepositoryOuterface(Outerface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, table_config:DataTableConfig, export_modes:Set[ExportMode | AggregationMode],
                 dataset_key:str | DatasetKey,       with_zipping:bool=True,
                 connector:Optional[DatasetRepositoryConnector]=None):
        super().__init__(table_config=table_config, export_modes=export_modes)

        self._connector    : DatasetRepositoryConnector
        self._dataset_key  : DatasetKey = dataset_key if isinstance(dataset_key, DatasetKey) else DatasetKey.FromString(dataset_key)
        self._with_zipping : bool       = with_zipping
        if isinstance(connector, DatasetRepositoryConnector):
            self._connector = connector
        elif isinstance(self.Config.StoreConfig, DatasetRepositoryConfig):
            self._connector = DatasetRepositoryConnector(
                config=self.Config.StoreConfig,
                with_zipping=self._with_zipping
            )
        else:
            raise ValueError(f"DatasetRepository config was for a connector other than a dataset repository! Found config type {type(self.Config.StoreConfig)}")
        if self.Connector.StoreConfig.IsRemote:
            raise NotImplementedError(f"Could not create outerface! The configured dataset repository at {self.Connector.StoreConfig.Location} is a remote repository, and writing to remote repositories is not yet supported.")
        else:
            self.Connector.Open()

            dataset = self.Connector.GetDatasetSchema(
                dataset_id=dataset_key if isinstance(dataset_key, DatasetKey) else DatasetKey.FromString(dataset_key),
                create=True
            )

            self._all_events    = self._getOuterface(file_type="all-events",          path=dataset.AllEventsFile()        if dataset else None, export_modes=export_modes)
            self._game_events   = self._getOuterface(file_type="game-events",         path=dataset.GameEventsFile()       if dataset else None, export_modes=export_modes)
            self._all_feats     = self._getOuterface(file_type="combined-features",   path=dataset.CombinedFeaturesFile() if dataset else None, export_modes=export_modes)
            self._session_feats = self._getOuterface(file_type="session-features",    path=dataset.SessionsFile()         if dataset else None, export_modes=export_modes)
            self._player_feats  = self._getOuterface(file_type="player-features",     path=dataset.PlayersFile()          if dataset else None, export_modes=export_modes)
            self._pop_feats     = self._getOuterface(file_type="population-features", path=dataset.PopulationFile()       if dataset else None, export_modes=export_modes)

    @property
    def Connector(self) -> DatasetRepositoryConnector:
        return self._connector

    # *** IMPLEMENT ABSTRACTS ***

    @override
    def _removeExportMode(self, mode:ExportMode | AggregationMode):
        match mode:
            case ExportMode.EVENTS:
                self._all_events = None
                self._game_events = None
            case ExportMode.FEATURES:
                self._all_feats = None
            case AggregationMode.SESSION:
                self._session_feats = None
            case AggregationMode.PLAYER:
                self._player_feats = None
            case AggregationMode.POPULATION:
                self._pop_feats = None
        return

    @override
    def _setupGameEventsTable(self, header:List[str]) -> None:
        if self._game_events:
            self._game_events._setupGameEventsTable(header=header)

    @override
    def _setupDetectorEventsTable(self, header:List[str]) -> None:
        if self._all_events:
            self._all_events._setupDetectorEventsTable(header=header)

    @override
    def _setupAllFeaturesTable(self, header:List[str]) -> None:
        if self._all_feats:
            self._all_feats._setupAllFeaturesTable(header=header)

    @override
    def _setupSessionTable(self, header:List[str]) -> None:
        if self._session_feats:
            self._session_feats._setupSessionTable(header=header)

    @override
    def _setupPlayerTable(self, header:List[str]) -> None:
        if self._player_feats:
            self._player_feats._setupPlayerTable(header=header)

    @override
    def _setupPopulationTable(self, header:List[str]) -> None:
        if self._pop_feats:
            self._pop_feats._setupPopulationTable(header=header)

    @override
    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        if self._game_events:
            self._game_events._writeGameEventLines(events=events)

    @override
    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        if self._all_events:
            self._all_events._writeAllEventLines(events=events)

    @override
    def _writeAllFeatureLines(self, feature_lines:List[ExportRow]) -> None:
        if self._all_feats:
            self._all_feats._writeAllFeatureLines(feature_lines=feature_lines)

    @override
    def _writeSessionLines(self, session_lines:List[ExportRow]) -> None:
        if self._session_feats:
            self._session_feats._writeSessionLines(session_lines=session_lines)

    @override
    def _writePlayerLines(self, player_lines:List[ExportRow]) -> None:
        if self._player_feats:
            self._player_feats._writePlayerLines(player_lines=player_lines)

    @override
    def _writePopulationLines(self, population_lines:List[ExportRow]) -> None:
        if self._pop_feats:
            self._pop_feats._writePopulationLines(population_lines=population_lines)

    @override
    def _writeMetadata(self, dataset_schema:DatasetSchema):
        game_dir = self._repository.LocalDirectory.FolderPath / self._dataset_key.GameID
        try:
            game_dir.mkdir(exist_ok=True, parents=True)
        except Exception as err:
            msg = f"Could not set up folder {game_dir}. {type(err)} {str(err)}"
            Logger.Log(msg, logging.WARNING)
        else:
            self._writeMetadataFile(dataset_schema=dataset_schema)
            if isinstance(self._repository.Location, DirectoryLocationConfig):
                _local_dir = self._repository.Location
                _public_url = None
            else: # we got a URL base
                _local_dir = None
                _public_url = self._repository.Location
            _file_index = RepositoryLocationConfig(name="IndexingConfig",
                                             local_dir=_local_dir,
                                             public_url=_public_url,
                                             templates_url=URLLocationConfig.FromDict(name="TemplateURL", unparsed_elements={"URL" : self._repository.TemplatesBase.Location})
            )
            self._updateFileExportList(file_indexing=_file_index, dataset_schema=dataset_schema)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _getOuterface(self, file_type:str, path:Optional[str], export_modes:Set[ExportMode | AggregationMode]) -> Optional[CSVOuterface]:
        ret_val : Optional[CSVOuterface] = None

        if path:
            cfg_name = f"{self.Config.Name}-{file_type}"
            ret_val = CSVOuterface(
                table_config=DataTableConfig(
                    name=cfg_name,
                    store=self.Config.StoreConfig,
                    table_schema=self.Config.TableSchema,
                    table_location=FileLocationConfig.FromPath(name=f"{cfg_name}-location", fullpath=path)
                ),
                export_modes=export_modes,
                store=None
            )

        return ret_val

    ## Public function to write out a tiny metadata file for indexing OGD data files.
    #  Using the paths of the exported files, and given some other variables for
    #  deriving file metadata, this simply outputs a new file_name.meta file.
    #  @param date_range    The range of dates included in the exported data.
    #  @param num_sess      The number of sessions included in the recent export.
    def _writeMetadataFile(self, dataset_schema:DatasetSchema) -> None:
        game_dir = self._repository.LocalDirectory.FolderPath / self._dataset_key.GameID
        match_string = f"{self._dataset_key}_\\w*\\.meta"
        old_metas = [f for f in os.listdir(game_dir) if re.match(match_string, f)]
        for old_meta in old_metas:
            try:
                Logger.Log(f"Removing old meta file, {old_meta}")
                os.remove(game_dir / old_meta)
            except Exception as err:
                msg = f"Could not remove old meta file {old_meta}. {type(err)} {str(err)}"
                Logger.Log(msg, logging.WARNING)
        # Third, write the new meta file.
        # calculate the path and name of the metadata file, and open/make it.
        meta_file_path : Path = game_dir / f"{self._dataset_key}_{self._generateHash()}.meta"
        with open(meta_file_path, "w", encoding="utf-8") as meta_file :
            meta_file.write(json.dumps(dataset_schema.AsMetadata, indent=4))
            meta_file.close()

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

    # ******* STUFF THAT GOES UP TO PROCESSING LEVEL *********

    @staticmethod
    def _generateHash():
        ret_val    : str  = ""
        # get hash
        try:
            repo = Repo(search_parent_directories=True)
            if repo.git is not None:
                ret_val = str(repo.git.rev_parse(repo.head.object.hexsha, short=7))
        except InvalidGitRepositoryError as err:
            msg = f"Code is not in a valid Git repository:\n{str(err)}"
            Logger.Log(msg, logging.ERROR)
        except NoSuchPathError as err:
            msg = f"Unable to access proper file paths for Git repository:\n{str(err)}"
            Logger.Log(msg, logging.ERROR)

        return ret_val


    ## Public function to update the list of exported files.
    #  Using the paths of the exported files, and given some other variables for
    #  deriving file metadata, this simply updates the JSON file to the latest
    #  list of files.
    #  @param date_range    The range of dates included in the exported data.
    #  @param num_sess      The number of sessions included in the recent export.
    def _updateFileExportList(self, file_indexing:RepositoryLocationConfig, dataset_schema:DatasetSchema) -> None:
        if self._repository.LocalDirectory is not None:
            DatasetRepositoryOuterface._backupFileExportList(self._repository.LocalDirectory.FolderPath)
            file_index = {}
            existing_datasets = {}
            try:
                file_index = fileio.loadJSONFile(filename="file_list.json", path=self._repository.LocalDirectory.FolderPath)
            except FileNotFoundError:
                Logger.Log("file_list.json does not exist.", logging.WARNING)
            except json.decoder.JSONDecodeError as err:
                Logger.Log(f"file_list.json has invalid format: {str(err)}.", logging.WARNING)
            finally:
                if not "CONFIG" in file_index.keys():
                    Logger.Log("No CONFIG found in file_list.json, adding default CONFIG...", logging.WARNING)
                    file_index["CONFIG"] = {
                        "files_base" : file_indexing.PublicURL,
                        "templates_base" : file_indexing.TemplatesURL
                    }
                if not dataset_schema.Key.GameID in file_index.keys():
                    file_index[dataset_schema.Key.GameID] = {}
                existing_datasets  = file_index[dataset_schema.Key.GameID]
                with open(self._repository.LocalDirectory.FolderPath / "file_list.json", "w") as existing_csv_file:
                    Logger.Log(f"Opened file list for writing at {existing_csv_file.name}", logging.INFO)
                    existing_metadata = existing_datasets.get(dataset_schema.DatasetID, {})
                    new_meta = dataset_schema.AsMetadata
                    new_meta["population_file"] = new_meta["population_file"]   or existing_metadata.get("population_file", existing_metadata.get("population"))
                    new_meta["players_file"] = new_meta["players_file"]         or existing_metadata.get("players_file",    existing_metadata.get("players"))
                    new_meta["sessions_file"] = new_meta["sessions_file"]       or existing_metadata.get("sessions_file",   existing_metadata.get("sessions"))
                    new_meta["game_events_file"] = new_meta["game_events_file"] or existing_metadata.get("game_events",     existing_metadata.get("events", existing_metadata.get("raw_events")))
                    new_meta["all_events_file"] = new_meta["all_events_file"]   or existing_metadata.get("all_events",      existing_metadata.get("processed_events"))
                    file_index[dataset_schema.Key.GameID][dataset_schema.DatasetID] = new_meta
                    existing_csv_file.write(json.dumps(file_index, indent=4))
        else:
            Logger.Log(f"Could not update file export list, repository {self} does not have a local directory", logging.WARNING)

    @staticmethod
    def _backupFileExportList(data_dir:Path) -> bool:
        try:
            src  : Path = data_dir / "file_list.json"
            dest : Path = data_dir / "file_list.json.bak"
            if src.exists():
                shutil.copyfile(src=src, dst=dest)
            else:
                Logger.Log("Could not back up file_list.json, because it does not exist!", logging.WARN)
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            Logger.Log(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            return False
        else:
            Logger.Log(f"Backed up file_list.json to {dest}", logging.INFO)
            return True
