# standard imports
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Dict, Optional, TypeAlias

# ogd imports
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.EmptyCredential import EmptyCredential
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.schemas.locations.DirectoryLocationSchema import DirectoryLocationSchema
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.utils.typing import Map

BaseLocation : TypeAlias = URLLocationSchema | DirectoryLocationSchema

# Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.
class DatasetRepositoryConfig(DataStoreConfig):
    """Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.

    It also expects to track a mapping of game names to collections of datasets, under a "datasets" key.
    Then the structure is like:

    ```
    {
        "files_base" : "path/to/folder/"
        "templates_base" : "URL/to/templates/"
        "datasets" : {
            "GAME_NAME" : {
                "DATASET_START_to_END" : { ... },
                "DATASET_START_to_END" : { ... },
                ...
            }
            ...
        }
    }
    ```
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_FILE_BASE = DirectoryLocationSchema(
        name="DefaultRepositoryLocation",
        folder_path=Path("./data"),
        other_elements=None
    )
    _DEFAULT_TEMPLATE_BASE = URLLocationSchema(
        name="DefaultTemplatesBase",
        url=urlparse("https://github.com/opengamedata/opengamedata-samples"),
        other_elements=None
    )
    _DEFAULT_DATASETS = {}

    def __init__(self, name:str,
                 # params for class
                 files_base:BaseLocation,
                 templates_base:BaseLocation,
                 datasets:Dict[str, DatasetCollectionSchema],
                 # params for parent
                 store_type:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._files_base     : BaseLocation = files_base     or self._parseFilesBase(unparsed_elements=unparsed_elements)
        self._templates_base : BaseLocation = templates_base or self._parseTemplatesBase(unparsed_elements=unparsed_elements)
        self._datasets       : Dict[str, DatasetCollectionSchema] = datasets or self._parseDatasets(unparsed_elements=unparsed_elements)
        super().__init__(name=name, store_type="Repository", other_elements=other_elements)

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def FilesBase(self) -> BaseLocation:
        """Property for the base 'path' to a set of dataset files.
        May be an actual path, or a base URL for accessing from a file server.

        :return: _description_
        :rtype: Optional[str]
        """
        return self._files_base

    @property
    def TemplatesBase(self) -> BaseLocation:
        return self._templates_base

    @property
    def Games(self) -> Dict[str, DatasetCollectionSchema]:
        return self._datasets

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @property
    def Location(self) -> BaseLocation:
        return self.FilesBase

    @property
    def Credential(self) -> EmptyCredential:
        return EmptyCredential.Default()

    @property
    def AsConnectionInfo(self) -> str:
        return f"{self.Name} : {self.Location.Location}"

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "DatasetRepositoryConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetRepositoryConfig
        """
        _files_base     : BaseLocation = cls._parseFilesBase(unparsed_elements=unparsed_elements)
        _templates_base : BaseLocation = cls._parseTemplatesBase(unparsed_elements=unparsed_elements)
        _datasets       : Dict[str, DatasetCollectionSchema] = cls._parseDatasets(unparsed_elements=unparsed_elements)

        _used = {"files_base", "templates_base"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return DatasetRepositoryConfig(name=name, files_base=_files_base, templates_base=_templates_base, datasets=_datasets, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetRepositoryConfig":
        return DatasetRepositoryConfig(
            name="CONFIG NOT FOUND",
            files_base=cls._DEFAULT_FILE_BASE,
            templates_base=cls._DEFAULT_TEMPLATE_BASE,
            datasets=cls._DEFAULT_DATASETS,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFilesBase(unparsed_elements:Map) -> BaseLocation:
        ret_val : BaseLocation

        raw_base = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["files_base"],
            to_type=str,
            default_value=DatasetRepositoryConfig._DEFAULT_FILE_BASE,
            remove_target=True
        )
        as_url = urlparse(raw_base)
        if as_url.scheme not in {"", "file"}:
            ret_val = URLLocationSchema(name="RepositoryFilesBase", url=as_url)
        else:
            ret_val = DirectoryLocationSchema(name="RepositoryFilesBase", folder_path=Path(raw_base))

        return ret_val

    @staticmethod
    def _parseTemplatesBase(unparsed_elements:Map) -> BaseLocation:
        return DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["templates_base"],
            to_type=str,
            default_value=DatasetRepositoryConfig._DEFAULT_TEMPLATE_BASE,
            remove_target=True
        )

    @staticmethod
    def _parseDatasets(unparsed_elements:Map) -> Dict[str, DatasetCollectionSchema]:
        ret_val : Dict[str, DatasetCollectionSchema]

        _data_elems = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["datasets"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if _data_elems:
            ret_val = {
                key : DatasetCollectionSchema.FromDict(name=key, unparsed_elements=datasets if isinstance(datasets, dict) else {})
                for key, datasets in _data_elems.items()
            }
        else:
            ret_val = DatasetRepositoryConfig._DEFAULT_DATASETS

        return ret_val

    # *** PRIVATE METHODS ***
