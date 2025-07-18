# standard imports
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# ogd imports
from ogd.common.configs.datasets.DatasetCollectionConfig import DatasetRepositoryConfig
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.datasets.GameDatasetCollectionSchema import GameDatasetCollectionSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

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

    def __init__(self, name:str, game_file_lists:Dict[str, GameDatasetCollectionSchema], file_list_config:DatasetRepositoryConfig, other_elements:Dict[str, Any]):
        self._games_file_lists : Dict[str, GameDatasetCollectionSchema] = game_file_lists
        self._config           : DatasetRepositoryConfig                = file_list_config

        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return self.Name

    @property
    def Games(self) -> Dict[str, GameDatasetCollectionSchema]:
        return self._games_file_lists
    @property
    def Config(self) -> DatasetRepositoryConfig:
        return self._config

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "DatasetCollectionSchema":
        _config           : DatasetRepositoryConfig                = cls._parseConfig(name=f"{name}Config", unparsed_elements=unparsed_elements)
        _games_file_lists : Dict[str, GameDatasetCollectionSchema] = cls._parseGamesFileLists(unparsed_elements=unparsed_elements)

        return DatasetCollectionSchema(name=name, game_file_lists=_games_file_lists, file_list_config=_config, other_elements={})

    @classmethod
    def Default(cls) -> "DatasetCollectionSchema":
        return DatasetCollectionSchema(
            name="DefaultDatasetCollectionSchema",
            game_file_lists=cls._DEFAULT_GAME_FILE_LISTS,
            file_list_config=DatasetRepositoryConfig.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseConfig(name:str, unparsed_elements:Map) -> DatasetRepositoryConfig:
        ret_val : DatasetRepositoryConfig

        _config_elem = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["CONFIG"],
            to_type=dict,
            default_value=DatasetRepositoryConfig.Default(),
            remove_target=True
        )
        # If parse gave us back a dict, then we pass it into the FromDict for config,
        # else assume it was the default value we can return directly.
        if isinstance(_config_elem, dict):
            ret_val = DatasetRepositoryConfig.FromDict(name=name, unparsed_elements=_config_elem)
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
