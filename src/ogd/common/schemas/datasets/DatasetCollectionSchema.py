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

# Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.
class DatasetCollectionConfig(Schema):
    """Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.

    This is a separate class from DatasetCollectionSchema because this config exists as its own sub-element of a `file_list.json` file.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_FILE_BASE = "https://fieldday-web.ad.education.wisc.edu/opengamedata/"
    _DEFAULT_TEMPLATE_BASE = "https://github.com/opengamedata/opengamedata-samples"

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
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "DatasetCollectionConfig":
        _files_base     : Optional[str]
        _templates_base : Optional[str]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} indexing config, all_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _files_base = cls._parseFilesBase(unparsed_elements=unparsed_elements)
        _templates_base = cls._parseTemplatesBase(unparsed_elements=unparsed_elements)
        _used = {"files_base", "templates_base"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return DatasetCollectionConfig(name=name, file_base_path=_files_base, template_base_path=_templates_base, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetCollectionConfig":
        return DatasetCollectionConfig(
            name="CONFIG NOT FOUND",
            file_base_path=cls._DEFAULT_FILE_BASE,
            template_base_path=cls._DEFAULT_TEMPLATE_BASE,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFilesBase(unparsed_elements:Map) -> str:
        return DatasetCollectionConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["files_base"],
            to_type=str,
            default_value=DatasetCollectionConfig._DEFAULT_FILE_BASE,
            remove_target=True
        )

    @staticmethod
    def _parseTemplatesBase(unparsed_elements:Map) -> str:
        return DatasetCollectionConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["templates_base"],
            to_type=str,
            default_value=DatasetCollectionConfig._DEFAULT_TEMPLATE_BASE,
            remove_target=True
        )

    # *** PRIVATE METHODS ***

# Simple class to manage a mapping of dataset names to dataset schemas.
class GameDatasetCollectionSchema(Schema):
    """Simple class to manage a mapping of dataset names to dataset schemas.

    This exists separately from `DatasetCollectionSchema` because there is,
    in turn, a map of game IDs to these collections.
    It's obviously more convenient code-wise not to have a dict of dicts of datasets directly in `DatasetCollectionSchema`.
    """
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
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "GameDatasetCollectionSchema":
        _game_datasets : Dict[str, DatasetSchema]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} game dataset collection, all_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _game_datasets = cls._parseGameDatasets(datasets=unparsed_elements)
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
    def _parseGameDatasets(unparsed_elements:Map) -> Dict[str, DatasetSchema]:
        ret_val : Dict[str, DatasetSchema]

        datasets = { key : DatasetSchema.FromDict(name=key, unparsed_elements=val) for key,val in unparsed_elements.items() }
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

class DatasetCollectionSchema(Schema):
    """_summary_

    TODO : The way this is structured and parsed from a dict is weird, need to see if there's a better way.

    :param Schema: _description_
    :type Schema: _type_
    :return: _description_
    :rtype: _type_
    """
    _DEFAULT_GAME_FILE_LISTS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_file_lists:Dict[str, GameDatasetCollectionSchema], file_list_config:DatasetCollectionConfig, other_elements:Dict[str, Any]):
        self._games_file_lists : Dict[str, GameDatasetCollectionSchema] = game_file_lists
        self._config           : DatasetCollectionConfig                   = file_list_config

        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return self.Name

    @property
    def Games(self) -> Dict[str, GameDatasetCollectionSchema]:
        return self._games_file_lists
    @property
    def Config(self) -> DatasetCollectionConfig:
        return self._config

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "DatasetCollectionSchema":
        _games_file_lists : Dict[str, GameDatasetCollectionSchema]
        _config           : DatasetCollectionConfig

        if not isinstance(all_elements, dict):
            all_elements = {}
    # 1. Parse config
        _config = DatasetSchema.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["CONFIG"],
            to_type=cls._parseConfig,
            default_value=DatasetCollectionConfig.Default()
        )
    # 2. Parse games
        _used = {"CONFIG"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        _games_file_lists = cls._parseGamesFileLists(games_dict=_leftovers)
        return DatasetCollectionSchema(name=name, game_file_lists=_games_file_lists, file_list_config=_config, other_elements={})

    @classmethod
    def Default(cls) -> "DatasetCollectionSchema":
        return DatasetCollectionSchema(
            name="DefaultDatasetCollectionSchema",
            game_file_lists=cls._DEFAULT_GAME_FILE_LISTS,
            file_list_config=DatasetCollectionConfig.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseConfig(config) -> DatasetCollectionConfig:
        ret_val : DatasetCollectionConfig
        if isinstance(config, dict):
            ret_val = DatasetCollectionConfig.FromDict(name="ConfigSchema", all_elements=config)
        else:
            ret_val = DatasetCollectionConfig.Default()
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
