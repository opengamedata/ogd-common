## import standard libraries
from typing import Any, Dict, Final, Optional, Self
## import local files
from ogd.common.configs.locations.LocationConfig import LocationConfig
from ogd.common.models.DatasetKey import DatasetKey
from ogd.common.utils.typing import JSONMap, Map

## @class DatabaseLocationConfig
class RepositoryLocationConfig(LocationConfig):
    """Class to encode the location of data within a dataset repository.

    In particular, it tracks the game ID and the dataset ID used to locate an individual dataset within a repository.

    NOTE : Not related to other location config class that previously encoded location of a repository itself.
    """

    _DEFAULT_GAME_ID    : Final[str] = "UNKNOWN_GAME"
    _DEFAULT_DATASET_ID : Final[str] = "UNKNOWN_DATASET"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:Optional[str], dataset_id:Optional[DatasetKey | str], other_elements:Optional[Map]=None):
        """Constructor for the `RepositoryLocationConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "game"    : "THE_GAME_ID",
            "dataset" : "THE_DATASET_ID"
        },
        ```

        :param name: _description_
        :type name: str
        :param database_name: _description_
        :type database_name: Optional[str]
        :param table_name: _description_
        :type table_name: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._game_id    : str        = self._getGameID(raw_val=game_id, unparsed_elements=unparsed_elements, schema_name=name)
        self._dataset_id : DatasetKey = self._getDatasetID(raw_val=dataset_id, unparsed_elements=unparsed_elements, schema_name=name)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def GameID(self) -> str:
        """The name of the database, within a DB system, where the table is located.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._game_id

    @property
    def DatasetID(self) -> DatasetKey:
        return self._dataset_id

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return f"{self.GameID}/{self.DatasetID}"

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.GameID}/{self.DatasetID}"
        return ret_val

    @property
    def AsDict(self) -> JSONMap:
        return {
            "game":self.GameID,
            "dataset":str(self.DatasetID)
        }

    @classmethod
    def Default(cls) -> "RepositoryLocationConfig":
        return RepositoryLocationConfig(
            name="DefaultDatabaseLocation",
            game_id=cls._DEFAULT_GAME_ID,
            dataset_id=cls._DEFAULT_DATASET_ID,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map,
                  key_overrides:Optional[Dict[str, str]]=None,
                  default_override:Optional[Self]=None)-> "RepositoryLocationConfig":
        """Create a RepositoryLocationConfig from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: RepositoryLocationConfig
        """
        return RepositoryLocationConfig(name=name, game_id=None, dataset_id=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _getGameID(raw_val:Any, unparsed_elements:Map,
                         schema_name:Optional[str]=None) -> str:

        return RepositoryLocationConfig.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["game", "game_id"],
            to_type=str,
            default_value=RepositoryLocationConfig._DEFAULT_GAME_ID,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _getDatasetID(raw_val:Any, unparsed_elements:Map,
                      schema_name:Optional[str]=None) -> DatasetKey:
        ret_val : DatasetKey

        raw_val = RepositoryLocationConfig.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["dataset", "dataset_id"],
            to_type=[DatasetKey, str],
            default_value=RepositoryLocationConfig._DEFAULT_DATASET_ID,
            remove_target=True,
            optional_element=True,
            schema_name=schema_name
        )
        match raw_val:
            case DatasetKey():
                ret_val = raw_val
            case str():
                ret_val = DatasetKey.FromString(raw_val)

        return ret_val
