# standard imports
import logging
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
            _msg = f"For {name} indexing config, unparsed_elements was not a dict, defaulting to empty dict"
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
            _msg = f"For {name} game dataset collection, unparsed_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _game_datasets = cls._parseGameDatasets(unparsed_elements=unparsed_elements)
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

        ret_val = {
            key : DatasetSchema.FromDict(name=key, unparsed_elements=val)
            for key,val in unparsed_elements.items()
        }

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
        self._config           : DatasetCollectionConfig                = file_list_config

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
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "DatasetCollectionSchema":
        _games_file_lists : Dict[str, GameDatasetCollectionSchema]
        _config           : DatasetCollectionConfig

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} dataset collection schema, unparsed_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _config = DatasetCollectionSchema._parseConfig(name=f"{name}Config", unparsed_elements=unparsed_elements)
        _games_file_lists = cls._parseGamesFileLists(unparsed_elements=unparsed_elements)

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
    def _parseConfig(name:str, unparsed_elements:Map) -> DatasetCollectionConfig:
        ret_val : DatasetCollectionConfig

        _config_elem = DatasetCollectionConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["CONFIG"],
            to_type=dict,
            default_value=DatasetCollectionConfig.Default(),
            remove_target=True
        )
        # If parse gave us back a dict, then we pass it into the FromDict for config,
        # else assume it was the default value we can return directly.
        if isinstance(_config_elem, dict):
            ret_val = DatasetCollectionConfig.FromDict(name=name, unparsed_elements=_config_elem)
        else:
            ret_val = _config_elem

        return ret_val

    @staticmethod
    def _parseGamesFileLists(unparsed_elements:Map) -> Dict[str, GameDatasetCollectionSchema]:
        ret_val : Dict[str, GameDatasetCollectionSchema]
        ret_val = {
            key : GameDatasetCollectionSchema.FromDict(key, datasets if isinstance(datasets, dict) else {})
            for key, datasets in unparsed_elements.items()
        }
        return ret_val

    # *** PRIVATE METHODS ***
