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
from ogd.common.configs.locations.RepositoryLocationConfig import RepositoryLocationConfig
from ogd.common.models.features.AggregationMode import AggregationMode
from ogd.common.models.features.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.configs.locations.FileLocationConfig import FileLocationConfig
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

    def __init__(self, repository_location:RepositoryLocationConfig | DirectoryLocationConfig | FileLocationConfig | URLLocationConfig,
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

        self._loc          : RepositoryLocationConfig
        self._remote_repo  : bool
        match repository_location:
            case DirectoryLocationConfig():
                self._loc = RepositoryLocationConfig(name=repository_location.Name, local_dir=repository_location, public_url=None, templates_url=None)
                self._remote_repo = False
            case FileLocationConfig():
                self._loc = RepositoryLocationConfig(name=repository_location.Name, local_dir=repository_location.Folder, public_url=None, templates_url=None)
                self._remote_repo = False
            case URLLocationConfig():
                self._loc = RepositoryLocationConfig(name=repository_location.Name, local_dir=None, public_url=repository_location, templates_url=None)
                self._remote_repo = True # if we got a URL, then we're connecting to a remote repo.

    # *** PROPERTIES ***

    @property
    def StoreConfig(self) -> DatasetRepositoryConfig:
        match self._config:
            case DatasetRepositoryConfig():
                return self._config
            case None:
                raise ValueError(f"DatasetRepositoryConnector for {self.ResourceName} has not been opened, so it does not have a config yet!")

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, writeable:bool=True) -> bool:
        ret_val : bool = False

        if self._remote_repo:
            with urlrequest.urlopen(url=self._loc.Location, data=None) as response:
                with json.loads(response) as remote_cfg:
                    self._config = DatasetRepositoryConfig.FromDict(
                        name=f"{self.ResourceName}Config",
                        unparsed_elements=remote_cfg
                    )
            ret_val = True
        else:
            self._config = DatasetRepositoryConfig.FromFile(
                file_name="file_list.json",
                directory=self._loc.Location
            )
            ret_val = True

        return ret_val

    def _close(self) -> bool:
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
