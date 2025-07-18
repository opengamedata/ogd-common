# standard imports
import logging
from typing import Any, Dict

# ogd imports
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

# local imports
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

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
        unparsed_elements : Map = other_elements or {}

        self._game_datasets : Dict[str, DatasetSchema] = game_datasets or self._parseGameDatasets(unparsed_elements=unparsed_elements)

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
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "GameDatasetCollectionSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: GameDatasetCollectionSchema
        """
        _game_datasets : Dict[str, DatasetSchema] = cls._parseGameDatasets(unparsed_elements=unparsed_elements)

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
