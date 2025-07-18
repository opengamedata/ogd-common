# standard imports
from typing import Any, Dict, Optional

# ogd imports
from ogd.common.schemas.Schema import Schema

# local imports
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

# Simple class to manage a mapping of dataset names to dataset schemas.
class DatasetCollectionSchema(Schema):
    """Simple class to manage a mapping of dataset names to dataset schemas.

    This exists separately from `DatasetCollectionSchema` because there is,
    in turn, a map of game IDs to these collections.
    It's obviously more convenient code-wise not to have a dict of dicts of datasets directly in `DatasetCollectionSchema`.
    """
    _DEFAULT_DATASETS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, datasets:Dict[str, DatasetSchema], other_elements:Dict[str, Any]):
        unparsed_elements : Map = other_elements or {}

        self._datasets : Dict[str, DatasetSchema] = datasets or self._parseDatasets(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def Datasets(self) -> Dict[str, DatasetSchema]:
        return self._datasets

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "DatasetCollectionSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetCollectionSchema
        """
        _game_datasets : Dict[str, DatasetSchema] = cls._parseDatasets(unparsed_elements=unparsed_elements)

        return DatasetCollectionSchema(name=name, datasets=_game_datasets, other_elements={})

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetCollectionSchema":
        return DatasetCollectionSchema(
            name="DefaultDatasetCollectionSchema",
            datasets=cls._DEFAULT_DATASETS,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseDatasets(unparsed_elements:Map) -> Dict[str, DatasetSchema]:
        ret_val : Dict[str, DatasetSchema]

        ret_val = {
            key : DatasetSchema.FromDict(name=key, unparsed_elements=val)
            for key,val in unparsed_elements.items()
        }

        return ret_val

    # *** PRIVATE METHODS ***
