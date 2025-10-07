## import standard libraries
from typing import Dict, Final, List, Optional, Self
## import local files
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.typing import Map

## @class DirectoryLocationSchema
class RepositoryLocationSchema(LocationSchema):
    """Class to encode the location of a dataset within a repository.

    Practically, this just means specifying a dataset using the DatasetKey model class,
    allowing us to look up the file location(s) for a dataset within a repository directory structure.
    """

    _DEFAULT_KEY : Final[DatasetKey] = DatasetKey(game_id="UNKNOWN_GAME", from_date="1/1/2020", to_date="1/31/2020")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 dataset:Optional[DatasetKey | str],
                 other_elements:Optional[Map]=None):
        """Constructor for the `RepositoryLocationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.
        Since `DatasetKey` does not have a true `FromDict`,
        the `other_elements` will simply be treated as a kwargs and passed to the `DatasetKey` constructor.

        Expected format:

        ```
        {
            "folder": "path/to/folder"
        },
        ```

        :param name: _description_
        :type name: str
        :param folder_path: _description_
        :type folder_path: Optional[Path]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        fallbacks : Map = other_elements or {}

        self._dataset = self._toDatasetKey(dataset=dataset, fallbacks=fallbacks)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Key(self) -> DatasetKey:
        """The path of the folder containing the file located by this schema.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._dataset

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return str(self._dataset)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self._dataset}"
        return ret_val

    @classmethod
    def Default(cls) -> "RepositoryLocationSchema":
        return RepositoryLocationSchema(
            name="DefaultRepositoryLocation",
            dataset=RepositoryLocationSchema._DEFAULT_KEY,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "RepositoryLocationSchema":
        """Create a RepositoryLocationSchema from a given dictionary

        This implementation assumes the unparsed elements constitute the kwargs expected by the DatasetKey constructor.
        As such, it does not use overrides.

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :param key_overrides: _description_, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :param default_override: _description_, defaults to None
        :type default_override: Optional[Self], optional
        :return: _description_
        :rtype: DirectoryLocationSchema
        """
        _dataset = cls._parseDatasetKey(unparsed_elements=unparsed_elements)
        return RepositoryLocationSchema(name=name, dataset=_dataset, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    @staticmethod
    def FromString(name:str, key:str) -> "RepositoryLocationSchema":
        return RepositoryLocationSchema(name=name, dataset=key)

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toDatasetKey(dataset:Optional[DatasetKey | str], fallbacks:Map) -> DatasetKey:
        ret_val : DatasetKey
        if isinstance(dataset, DatasetKey):
            ret_val = dataset
        elif isinstance(dataset, str):
            ret_val = DatasetKey.FromString(dataset)
        else:
            ret_val = RepositoryLocationSchema._parseDatasetKey(unparsed_elements=fallbacks)
        return ret_val

    @staticmethod
    def _parseDatasetKey(unparsed_elements:Map) -> DatasetKey:
        """Parse a DatasetKey from a dictionary of unparsed elements.

        This function assumes the unparsed elements constitute the kwargs expected by the DatasetKey constructor.
        As such, it does not accept overrides.
        It is a very naive version of a standard parsing function in a schema class.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: DatasetKey
        """
        return DatasetKey(**unparsed_elements)
