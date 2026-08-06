import json
import logging
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

        self._config       : DatasetRepositoryConfig
        self._with_zipping : bool = with_zipping
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
        return True

    def _close(self) -> bool:
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def GetDatasetSchema(self, game_id:str, dataset_id:DatasetKey) -> Optional[DatasetSchema]:
        return self.StoreConfig.Games.get(game_id, {}).get(str(dataset_id))

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
