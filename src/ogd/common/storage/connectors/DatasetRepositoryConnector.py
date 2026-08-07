import json
import logging
import shutil
from pathlib import Path
from typing import Optional
from urllib import request as urlrequest
from urllib.error import URLError
## import local files
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.configs.locations.FileLocationConfig import FileLocationConfig
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.models.features.AggregationMode import AggregationMode
from ogd.common.models.features.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.Logger import Logger

class DatasetRepositoryConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***
    _DEFAULT_EXTENSION = "tsv"
    _FILE_SUFFIXES     = {ExportMode.EVENTS.name:"game-events", ExportMode.DETECTORS.name:"all-events",
                          ExportMode.FEATURES.name:"all-features", AggregationMode.SESSION.name:"session-features",
                          AggregationMode.PLAYER.name:"player-features", AggregationMode.POPULATION.name:"population-features"}

    def __init__(self, config: DatasetRepositoryConfig | DirectoryLocationConfig | FileLocationConfig | URLLocationConfig,
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

        self._config           : DatasetRepositoryConfig
        self._with_zipping     : bool = with_zipping
        self._has_new_datasets : bool = False
        match config:
            case DatasetRepositoryConfig():
                self._config = config
            case DirectoryLocationConfig():
                self._config = DatasetRepositoryConfig.FromFile(
                    file_name="file_list.json",
                    directory=config.FolderPath
                )
            case FileLocationConfig():
                self._config = DatasetRepositoryConfig.FromFile(
                    file_name=config.Filename,
                    directory=config.Folder
                )
            case URLLocationConfig():
                try:
                    with urlrequest.urlopen(url=config.Location, data=None) as response:
                        remote_cfg = json.loads(response.read())
                        self._config = DatasetRepositoryConfig.FromDict(
                            name=f"{config.Location}Config",
                            unparsed_elements=remote_cfg
                        )
                except URLError as err:
                    Logger.Log(f"Could not find dataset repository information at {config.Location}, failed to open connector to the repository!\nError message: {err}", logging.ERROR)

    # *** PROPERTIES ***

    @property
    def StoreConfig(self) -> DatasetRepositoryConfig:
        return self._config

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, writeable:bool=True) -> bool:
        """Perform an "open" o the repo connector.

        Always returns true, since the config is already loaded, with one exception:
        If opening as "writable," but configured for a remote-only repository, result is False because we do not yet support writing remote repos.

        :param writeable: Whether to open the connection with write permissions, defaults to True
        :type writeable: bool, optional
        :return: True if the function successfully opened a connection to the repository, otherwise False.
        :rtype: bool
        """
        ret_val : bool = True

        if writeable and self.StoreConfig.IsRemote:
            ret_val = False

        return ret_val

    def _close(self) -> bool:
        if self._has_new_datasets and not self.StoreConfig.IsRemote:
            self._updateFileExportList()
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def GetDatasetSchema(self, dataset_id:DatasetKey) -> Optional[DatasetSchema]:
        """Function to get the schema associated with a dataset within a repository.

        :param game_id: The game whose dataset we should be looking for.
        :type game_id: str
        :param dataset_id: _description_
        :type dataset_id: DatasetKey
        :param create: _description_
        :type create: bool
        :return: _description_
        :rtype: Optional[DatasetSchema]
        """
        return self.StoreConfig.Games.get(dataset_id.GameID, {}).get(str(dataset_id))

    def AddDatasetSchema(self, dataset:DatasetSchema):
        dataset_id = DatasetKey.FromString(dataset.DatasetID)
        if not dataset_id.GameID in self.StoreConfig.Games.keys():
            self.StoreConfig.Games[dataset_id.GameID] = DatasetCollectionSchema(name=dataset_id.GameID, datasets={}, other_elements={})
        self.StoreConfig.Games[dataset_id.GameID].Datasets[str(dataset_id)] = dataset
        self._has_new_datasets = True

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _updateFileExportList(self) -> None:
        """Update the list of datasets in original `file_list.json`.

        Using the paths of the exported files, and given some other variables for
        deriving file metadata, this simply updates the JSON file to the latest
        list of files.

        :param dataset_schema: _description_
        :type dataset_schema: DatasetSchema
        """
        repo_dir = self.StoreConfig.LocalDirectory

        if repo_dir:
            # 1. Back up the file_list before we update, in case we need to roll back for any reason.
            try:
                src  : Path = repo_dir.FolderPath / "file_list.json"
                dest : Path = repo_dir.FolderPath / "file_list.json.bak"
                if src.exists():
                    shutil.copyfile(src=src, dst=dest)
                else:
                    Logger.Log("Could not back up file_list.json, because it does not exist!", logging.WARN)
            except Exception as err:
                msg = f"{type(err)} {str(err)}"
                Logger.Log(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            else:
                Logger.Log(f"Backed up file_list.json to {dest}", logging.INFO)
            # 2. Write out the latest config to file_list.json
            with open(repo_dir.FolderPath / "file_list.json", "w") as dataset_index:
                dataset_index.write(json.dumps(self.StoreConfig.AsDict, indent=4))
        else:
            Logger.Log(f"Could not update file export list, repository {self} does not have a local directory", logging.WARNING)
