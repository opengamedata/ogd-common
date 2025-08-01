## import standard libraries
import json
import logging
import os
import re
import shutil
import sys
import traceback
from datetime import datetime
from git.repo import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from pathlib import Path
from typing import Any, Dict, IO, List, Optional, Set
# 3rd-party imports
import numpy as np
import pandas as pd
# import local files
# from ogd import games
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.IndexingConfig import FileIndexingConfig
from ogd.common.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.configs.storage.LocalDatasetRepositoryConfig import LocalDatasetRepositoryConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.schemas.events.LoggingSpecificationSchema import LoggingSpecificationSchema
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.storage.connectors.CSVConnector import CSVConnector
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.utils import fileio
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow
from ogd.common.utils.Readme import Readme

class CSVOuterface(Outerface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, export_modes:Set[ExportMode],
                 repository:LocalDatasetRepositoryConfig, dataset_id:str,
                 extension:str="tsv", with_separate_feature_files:bool=True, with_zipping:bool=True,
                 store:Optional[CSVConnector]=None):
        self._store : CSVConnector

        super().__init__(config=config, export_modes=export_modes)
        self._repository                  = repository
        self._dataset_id                  = dataset_id
        self._extension                   = extension
        self._with_separate_feature_files = with_separate_feature_files
        self._with_zipping                = with_zipping
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, FileStoreConfig):
            self._store = CSVConnector(config=self.Config.StoreConfig, extension=self._extension, with_secondary_files=set())
        else:
            raise ValueError(f"CSVInterface config was for a connector other than CSV/TSV files! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

        existing_datasets = {}
        try:
            file_directory = fileio.loadJSONFile(filename="file_list.json", path=self._repository.FilesBase.FolderPath)
            existing_datasets = file_directory.get(self.Config.GameID, {})
        except FileNotFoundError as err:
            Logger.Log("file_list.json does not exist.", logging.WARNING)
        except json.decoder.JSONDecodeError as err:
            Logger.Log(f"file_list.json has invalid format: {str(err)}.", logging.WARNING)
        existing_meta = existing_datasets.get(self._dataset_id, None)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, FileStoreConfig):
            self._store = CSVConnector(
                config               = self.Config.StoreConfig,
                extension            = self.Extension,
                with_secondary_files = export_modes if with_separate_feature_files else set(),
                with_zipping         = self._with_zipping,
                existing_meta        = existing_meta
            )
        else:
            raise ValueError(f"CSVInterface config was for a connector other than CSV/TSV files! Found config type {type(self.Config.StoreConfig)}")

        # then set up our paths, and ensure each exists.
        # finally, generate file names.

    @property
    def Connector(self) -> CSVConnector:
        return self._store

    @property
    def Extension(self) -> str:
        return self._extension

    @property
    def Delimiter(self) -> str:
        match self.Extension:
            case "tsv":
                return "\t"
            case "csv":
                return ","
            case _:
                Logger.Log(f"CSVOuterface has unexpected extension {self.Extension}, defaulting to comma-separation!", logging.WARN)
                return ","
        


    # *** IMPLEMENT ABSTRACTS ***

    def _removeExportMode(self, mode:ExportMode):
        self.Connector.RemoveSecondaryFile(mode=mode)

    def _writeGameEventsHeader(self, header:List[str]) -> None:
        cols = CSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        f = self.Connector.SecondaryFiles.get(ExportMode.EVENTS.name, None)
        if f is not None:
            f.writelines(cols_line)
        else:
            Logger.Log("No raw_events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writeAllEventsHeader(self, header:List[str]) -> None:
        cols = CSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        if self.Connector.File is not None:
            self.Connector.File.writelines(cols_line)
        else:
            Logger.Log("No processed_events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writeSessionHeader(self, header:List[str]) -> None:
        cols = CSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        f = self.Connector.SecondaryFiles.get(ExportMode.SESSION.name, None)
        if f is not None:
            f.writelines(cols_line)
        else:
            Logger.Log("No session file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writePlayerHeader(self, header:List[str]) -> None:
        cols = CSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        f = self.Connector.SecondaryFiles.get(ExportMode.PLAYER.name, None)
        if f is not None:
            f.writelines(cols_line)
        else:
            Logger.Log("No player file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writePopulationHeader(self, header:List[str]) -> None:
        cols = CSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        f = self.Connector.SecondaryFiles.get(ExportMode.POPULATION.name, None)
        if f is not None:
            f.writelines(cols_line)
        else:
            Logger.Log("No population file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        event_strs = [CSVOuterface._cleanSpecialChars(vals=[str(item) for item in event]) for event in events]
        event_lines = ["\t".join(event) + "\n" for event in event_strs]
        f = self.Connector.SecondaryFiles.get(ExportMode.EVENTS.name, None)
        if f is not None:
            f.writelines(event_lines)
        else:
            Logger.Log("No raw_events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(event_lines))

    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        event_strs = [CSVOuterface._cleanSpecialChars(vals=[str(item) for item in event]) for event in events]
        event_lines = ["\t".join(event) + "\n" for event in event_strs]
        f = self.Connector.SecondaryFiles.get(ExportMode.DETECTORS.name, None)
        if f is not None:
            f.writelines(event_lines)
        else:
            Logger.Log("No processed_events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(event_lines))

    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        # self._sess_count += len(sessions)
        _session_feats = [CSVOuterface._cleanSpecialChars(vals=sess) for sess in sessions]
        _session_lines = ["\t".join(sess) + "\n" for sess in _session_feats]
        f = self.Connector.SecondaryFiles.get(ExportMode.SESSION.name, None)
        if f is not None:
            f.writelines(_session_lines)
        else:
            Logger.Log("No session file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(_session_lines))

    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        _player_feats = [CSVOuterface._cleanSpecialChars(vals=play) for play in players]
        _player_lines = ["\t".join(play) + "\n" for play in _player_feats]
        f = self.Connector.SecondaryFiles.get(ExportMode.PLAYER.name, None)
        if f is not None:
            f.writelines(_player_lines)
        else:
            Logger.Log("No player file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(_player_lines))

    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        _pop_feats = [CSVOuterface._cleanSpecialChars(vals=pop) for pop in populations]
        _pop_lines = ["\t".join(pop) + "\n" for pop in _pop_feats]
        f = self.Connector.SecondaryFiles.get(ExportMode.POPULATION.name, None)
        if f is not None:
            f.writelines(_pop_lines)
        else:
            Logger.Log("No population file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(_pop_lines))

    def _writeMetadata(self, metadata:Dict[str, Any]):
        game_dir = self._repository.FilesBase.FolderPath / self.Config.GameID
        try:
            game_dir.mkdir(exist_ok=True, parents=True)
        except Exception as err:
            msg = f"Could not set up folder {game_dir}. {type(err)} {str(err)}"
            Logger.Log(msg, logging.WARNING)
        else:
            self._ensureReadmeExists()
            self._writeMetadataFile(meta=metadata)
            self._updateFileExportList(num_sess=self.SessionCount)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _cleanSpecialChars(vals:List[Any], tab_width:int=3) -> List[str]:
        # check all return values for strings, and ensure no newlines or tabs get through, as they could throw off our outputs.
        for i in range(len(vals)):
            vals[i] = str(vals[i]).replace('\n', ' ').replace('\t', ' '*tab_width)
        return vals

    # *** PRIVATE METHODS ***

    def _ensureReadmeExists(self) -> None:
        game_dir = self._repository.FilesBase.FolderPath / self.Config.GameID
        try:
            # before we zip stuff up, let's check if the readme is in place:
            readme = open(game_dir / "README.md", mode='r')
        except FileNotFoundError:
            # if not in place, generate the readme
            Logger.Log(f"Missing readme for {self.Config.GameID}, generating new readme...", logging.WARNING, depth=1)
            from ogd import games
            _games_path  = Path(games.__file__) if Path(games.__file__).is_dir() else Path(games.__file__).parent
            event_collection     : LoggingSpecificationSchema = LoggingSpecificationSchema.FromFile(schema_name=self.Config.GameID.upper(), schema_path=_games_path / self.Config.GameID / "schemas")
            generator_collection : GeneratorCollectionConfig  = GeneratorCollectionConfig.FromFile(schema_name=self.Config.GameID.upper(), schema_path=_games_path / self.Config.GameID / "schemas")
            readme = Readme(event_collection=event_collection, generator_collection=generator_collection, table_schema=self.Config.Table or TableSchema.Default())
            readme.ToFile(path=game_dir)
        else:
            # otherwise, readme is there, so just close it and move on.
            readme.close()
            Logger.Log(f"Successfully found, opened, and closed the README.md", logging.DEBUG, depth=1)

    ## Public function to write out a tiny metadata file for indexing OGD data files.
    #  Using the paths of the exported files, and given some other variables for
    #  deriving file metadata, this simply outputs a new file_name.meta file.
    #  @param date_range    The range of dates included in the exported data.
    #  @param num_sess      The number of sessions included in the recent export.
    def _writeMetadataFile(self, meta:Dict[str, Any]) -> None:
        game_dir = self._repository.FilesBase.FolderPath / self.Config.GameID
        match_string = f"{self._dataset_id}_\\w*\\.meta"
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
        meta_file_path : Path = game_dir / f"{self._dataset_id}_{self._generateHash()}.meta"
        with open(meta_file_path, "w", encoding="utf-8") as meta_file :
            meta_file.write(json.dumps(meta, indent=4))
            meta_file.close()

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
    def _updateFileExportList(self, file_indexing:FileIndexingConfig, dataset_schema:DatasetSchema) -> None:
        CSVOuterface._backupFileExportList(self._repository.FilesBase.FolderPath)
        file_index = {}
        existing_datasets = {}
        try:
            file_index = fileio.loadJSONFile(filename="file_list.json", path=self._repository.FilesBase.FolderPath)
        except FileNotFoundError as err:
            Logger.Log("file_list.json does not exist.", logging.WARNING)
        except json.decoder.JSONDecodeError as err:
            Logger.Log(f"file_list.json has invalid format: {str(err)}.", logging.WARNING)
        finally:
            if not "CONFIG" in file_index.keys():
                Logger.Log(f"No CONFIG found in file_list.json, adding default CONFIG...", logging.WARNING)
                file_index["CONFIG"] = {
                    "files_base" : file_indexing.RemoteURL,
                    "templates_base" : file_indexing.TemplatesURL
                }
            if not dataset_schema.Key.GameID in file_index.keys():
                file_index[dataset_schema.Key.GameID] = {}
            existing_datasets  = file_index[dataset_schema.Key.GameID]
            with open(self._repository.FilesBase.FolderPath / "file_list.json", "w") as existing_csv_file:
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

    @staticmethod
    def _backupFileExportList(data_dir:Path) -> bool:
        try:
            src  : Path = data_dir / "file_list.json"
            dest : Path = data_dir / "file_list.json.bak"
            if src.exists():
                shutil.copyfile(src=src, dst=dest)
            else:
                Logger.Log(f"Could not back up file_list.json, because it does not exist!", logging.WARN)
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            Logger.Log(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            return False
        else:
            Logger.Log(f"Backed up file_list.json to {dest}", logging.INFO)
            return True