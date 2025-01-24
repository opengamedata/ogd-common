# standard imports
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional

# ogd imports
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

# local imports
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

class FileListConfigSchema(Schema):

    # *** BUILT-INS & PROPERTIES ***

    DEFAULT_FILE_BASE = "https://fieldday-web.ad.education.wisc.edu/opengamedata/"
    DEFAULT_TEMPLATE_BASE = "https://github.com/opengamedata/opengamedata-samples"

    def __init__(self, name:str, file_base_path:Optional[str | Path], template_base_path:Optional[str | Path], other_elements:Optional[Map]=None):
        self._files_base     : Optional[str | Path] = file_base_path
        self._templates_base : Optional[str | Path] = template_base_path
        super().__init__(name=name, other_elements=other_elements)

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def FilesBase(self) -> Optional[str | Path]:
        """Property for the base 'path' to a set of dataset files.
        May be an actual path, or a base URL for accessing from a file server.

        :return: _description_
        :rtype: Optional[str]
        """
        return self._files_base
    @property
    def TemplatesBase(self) -> Optional[str | Path]:
        return self._templates_base

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "FileListConfigSchema":
        _files_base     : Optional[str]
        _templates_base : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} indexing config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _files_base = cls.ParseElement(all_elements=all_elements, logger=logger,
            valid_keys=["files_base"],
            value_type=cls._parseFilesBase,
            default_value=FileListConfigSchema.DEFAULT_FILE_BASE
        )
        _templates_base = cls.ParseElement(all_elements=all_elements, logger=logger,
            valid_keys=["templates_base"],
            value_type=cls._parseTemplatesBase,
            default_value=FileListConfigSchema.DEFAULT_TEMPLATE_BASE
        )
        _used = {"files_base", "templates_base"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return FileListConfigSchema(name=name, file_base_path=_files_base, template_base_path=_templates_base, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "FileListConfigSchema":
        return FileListConfigSchema(
            name="CONFIG NOT FOUND",
            file_base_path=cls.DEFAULT_FILE_BASE,
            template_base_path=cls.DEFAULT_TEMPLATE_BASE,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFilesBase(files_base) -> str:
        ret_val : str
        if isinstance(files_base, str):
            ret_val = files_base
        else:
            ret_val = str(files_base)
            Logger.Log(f"Filepath base was unexpected type {type(files_base)}, defaulting to str(files_name)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTemplatesBase(templates_base) -> str:
        ret_val : str
        if isinstance(templates_base, str):
            ret_val = templates_base
        else:
            ret_val = str(templates_base)
            Logger.Log(f"Templates base was unexpected type {type(templates_base)}, defaulting to str(templates_name)={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***

class GameDatasetCollectionSchema(Schema):
    _DEFAULT_DATASETS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_datasets:Dict[str, DatasetSchema], other_elements:Dict[str, Any]):
        self._game_datasets : Dict[str, DatasetSchema] = game_datasets

        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def Datasets(self) -> Dict[str, DatasetSchema]:
        return self._game_datasets

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "GameDatasetCollectionSchema":
        _game_datasets : Dict[str, DatasetSchema]

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} game dataset collection, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _game_datasets = cls._parseGameDatasets(datasets=all_elements)
        return GameDatasetCollectionSchema(name=name, game_datasets=_game_datasets, other_elements={})

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "GameDatasetCollectionSchema":
        return GameDatasetCollectionSchema(
            name="DefaultGameDatasetCollectionSchema",
            game_datasets=cls._DEFAULT_DATASETS,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseGameDatasets(datasets:Dict[str, Any]) -> Dict[str, DatasetSchema]:
        ret_val : Dict[str, DatasetSchema]
        if isinstance(datasets, dict):
            ret_val = {
                key : DatasetSchema.FromDict(key, dataset if isinstance(dataset, dict) else {})
                for key,dataset in datasets.items()
            }
        else:
            ret_val = {}
            Logger.Log(f"Collection of datasets was unexpected type {type(datasets)}, defaulting to empty dictionary.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***

class FileListSchema(Schema):
    """_summary_

    TODO : The way this is structured and parsed from a dict is weird, need to see if there's a better way.

    :param Schema: _description_
    :type Schema: _type_
    :return: _description_
    :rtype: _type_
    """
    _DEFAULT_GAME_FILE_LISTS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_file_lists:Dict[str, GameDatasetCollectionSchema], file_list_config:FileListConfigSchema, other_elements:Dict[str, Any]):
        self._games_file_lists : Dict[str, GameDatasetCollectionSchema] = game_file_lists
        self._config           : FileListConfigSchema                   = file_list_config

        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return self.Name

    @property
    def Games(self) -> Dict[str, GameDatasetCollectionSchema]:
        return self._games_file_lists
    @property
    def Config(self) -> FileListConfigSchema:
        return self._config

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "FileListSchema":
        _games_file_lists : Dict[str, GameDatasetCollectionSchema]
        _config           : FileListConfigSchema

        if not isinstance(all_elements, dict):
            all_elements = {}
    # 1. Parse config
        _config = DatasetSchema.ParseElement(all_elements=all_elements, logger=logger,
            valid_keys=["CONFIG"],
            value_type=cls._parseConfig,
            default_value=FileListConfigSchema.Default()
        )
    # 2. Parse games
        _used = {"CONFIG"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        _games_file_lists = cls._parseGamesFileLists(games_dict=_leftovers)
        return FileListSchema(name=name, game_file_lists=_games_file_lists, file_list_config=_config, other_elements={})

    @classmethod
    def Default(cls) -> "FileListSchema":
        return FileListSchema(
            name="DefaultFileListSchema",
            game_file_lists=cls._DEFAULT_GAME_FILE_LISTS,
            file_list_config=FileListConfigSchema.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseConfig(config) -> FileListConfigSchema:
        ret_val : FileListConfigSchema
        if isinstance(config, dict):
            ret_val = FileListConfigSchema.FromDict(name="ConfigSchema", all_elements=config)
        else:
            ret_val = FileListConfigSchema.Default()
            Logger.Log(f"Config was unexpected type {type(config)}, defaulting to empty ConfigSchema.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGamesFileLists(games_dict:Dict[str, Any]) -> Dict[str, GameDatasetCollectionSchema]:
        ret_val : Dict[str, GameDatasetCollectionSchema]
        if isinstance(games_dict, dict):
            ret_val = {
                key : GameDatasetCollectionSchema.FromDict(key, datasets if isinstance(datasets, dict) else {})
                for key, datasets in games_dict.items()
            }
        else:
            ret_val = {}
            Logger.Log(f"Collection of games was unexpected type {type(games_dict)}, defaulting to empty dictionary.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
