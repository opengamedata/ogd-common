# standard imports
from pathlib import Path
from typing import Any, Dict, Final, Optional, Self, TypeAlias

# ogd imports
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.EmptyCredential import EmptyCredential
from ogd.common.configs.locations.LocationConfig import LocationConfig
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.fileio import loadJSONFile
from ogd.common.utils.typing import JSONMap, Map

BaseLocation : TypeAlias = URLLocationConfig | DirectoryLocationConfig

class RepositoryLocationConfig(LocationConfig):
    _DEFAULT_LOCAL_DIR    : Final[DirectoryLocationConfig] = DirectoryLocationConfig(name="DefaultLocalDir", folder_path=Path("./data/"), other_elements={})
    _DEFAULT_PUB_URL_RAW  : Final[str]                     = "https://opengamedata.fielddaylab.wisc.edu/"
    _DEFAULT_PUBLIC_URL   : Final[URLLocationConfig]       = URLLocationConfig.FromString(name="DefaultRemoteURL", raw_url=_DEFAULT_PUB_URL_RAW)
    _DEFAULT_TEMPLATE_RAW : Final[str]                     = "https://github.com/opengamedata/opengamedata-samples"
    _DEFAULT_TEMPLATE_URL : Final[URLLocationConfig]       = URLLocationConfig.FromString(name="DefaultTemplateURL", raw_url=_DEFAULT_TEMPLATE_RAW)

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                local_dir:Optional[DirectoryLocationConfig | Map | Path | str],
                public_url:Optional[URLLocationConfig | Map | str],
                templates_url:Optional[URLLocationConfig | Map | str],
                other_elements:Optional[Map]=None):
        """Constructor for the `RepositoryLocationConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "LOCAL_DIR"     : "./data/",
            "PUBLIC_URL"    : "https://opengamedata.fielddaylab.wisc.edu/",
            "TEMPLATES_URL" : "https://github.com/opengamedata/opengamedata-samples"
        }
        ```

        :param name: _description_
        :type name: str
        :param local_dir: The local directory location of the repository.
        :type local_dir: Optional[Path]
        :param public_url: The URL at which this repository can be publicly accessed,
                        or None if the repository is not meant for public access.
        :type public_url: Optional[str]
        :param templates_url: A URL containing templates compatible with repository datasets.
        :type templates_url: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        fallbacks : Map = other_elements or {}

        self._local_dir     : Optional[DirectoryLocationConfig] = self._toLocalDir(local_dir=local_dir, fallbacks=fallbacks, schema_name=name)
        self._public_url    : Optional[URLLocationConfig]       = self._toPublicURL(public_url=public_url, fallbacks=fallbacks, schema_name=name)
        self._templates_url : URLLocationConfig                 = self._toTemplatesURL(templates_url=templates_url, fallbacks=fallbacks, schema_name=name)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Location(self) -> str:
        return str(self.LocalDirectory or self.PublicURL)

    @property
    def LocalDirectory(self) -> Optional[DirectoryLocationConfig]:
        return self._local_dir

    @property
    def PublicURL(self) -> Optional[URLLocationConfig]:
        """The public-facing URL at which this repository can be accessed.
        If the repository is not meant for public access, as is the case for local exports, this property returns None.

        :return: The public-facing URL at which this repository can be accessed, if any.
        :rtype: Optional[URLLocationSchema]
        """
        return self._public_url

    @property
    def TemplatesURL(self) -> URLLocationConfig:
        return self._templates_url

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def Default(cls) -> "RepositoryLocationConfig":
        return RepositoryLocationConfig(
            name            = "DefaultFileIndexingConfig",
            local_dir       = cls._DEFAULT_LOCAL_DIR,
            public_url      = cls._DEFAULT_PUBLIC_URL,
            templates_url   = cls._DEFAULT_TEMPLATE_URL,
            other_elements  = {}
        )

    @property
    def AsDict(self) -> JSONMap:
        return {
            "local_dir":self.LocalDirectory.AsDict if self.LocalDirectory is not None else None,
            "remote_url":self.PublicURL.AsDict if self.PublicURL is not None else None,
            "templates_url":self.TemplatesURL.AsDict
        }

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "RepositoryLocationConfig":
        """Create a file indexing Configuration from a dict.

        Expects dictionary to have the following form:
        ```json
        {
            "LOCAL_DIR"     : "./data/",
            "PUBLIC_URL"    : "https://opengamedata.fielddaylab.wisc.edu/",
            "TEMPLATES_URL" : "https://github.com/opengamedata/opengamedata-samples"
        }
        ```

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: FileIndexingConfig
        """
        return RepositoryLocationConfig(name=name, local_dir=None, public_url=None, templates_url=None, other_elements=unparsed_elements)


    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name} : Local=_{self.LocalDirectory}_, Remote=_{self.PublicURL}_"
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toLocalDir(local_dir:Optional[DirectoryLocationConfig | Map | Path | str], fallbacks:Map, schema_name:Optional[str]=None) -> Optional[DirectoryLocationConfig]:
        ret_val : Optional[DirectoryLocationConfig]
        if isinstance(local_dir, DirectoryLocationConfig):
            ret_val = local_dir
        elif isinstance(local_dir, dict):
            ret_val = DirectoryLocationConfig.FromDict(name=f"{schema_name}Directory", unparsed_elements=local_dir)
        elif isinstance(local_dir, str) or isinstance(local_dir, str):
            ret_val = DirectoryLocationConfig(name=f"{schema_name}Directory", folder_path=local_dir)
        else:
            ret_val = RepositoryLocationConfig._parseLocalDir(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _toPublicURL(public_url:Optional[URLLocationConfig | Map | str], fallbacks:Map, schema_name:Optional[str]=None) -> Optional[URLLocationConfig]:
        ret_val : Optional[URLLocationConfig]
        if isinstance(public_url, URLLocationConfig):
            ret_val = public_url
        elif isinstance(public_url, dict):
            ret_val = URLLocationConfig.FromDict(name=f"{schema_name}RemoteRepoURL", unparsed_elements=public_url)
        elif isinstance(public_url, str):
            ret_val = URLLocationConfig(name=f"{schema_name}RemoteRepoURL", url=public_url)
        else:
            ret_val = RepositoryLocationConfig._parseRemoteURL(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _toTemplatesURL(templates_url:Optional[URLLocationConfig | Map | str], fallbacks:Map, schema_name:Optional[str]=None) -> URLLocationConfig:
        ret_val : URLLocationConfig
        if isinstance(templates_url, URLLocationConfig):
            ret_val = templates_url
        elif isinstance(templates_url, dict):
            ret_val = URLLocationConfig.FromDict(name=f"{schema_name}TemplatesURL", unparsed_elements=fallbacks)
        elif isinstance(templates_url, str):
            ret_val = URLLocationConfig(name=f"{schema_name}TemplatesURL", url=templates_url)
        else:
            ret_val = RepositoryLocationConfig._parseTemplatesURL(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _parseLocalDir(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[DirectoryLocationConfig]:
        ret_val : Optional[DirectoryLocationConfig]

        raw_base = RepositoryLocationConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["files_base", "local_dir", "folder", "path"],
            to_type=[Path, dict],
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )
        if raw_base:
            if isinstance(raw_base, Path):
                ret_val = DirectoryLocationConfig(name=f"{schema_name}LocalDir", folder_path=raw_base)
            elif isinstance(raw_base, dict):
                ret_val = DirectoryLocationConfig.FromDict(name=f"{schema_name}LocalDir", unparsed_elements=raw_base)
            else:
                ret_val = RepositoryLocationConfig._DEFAULT_LOCAL_DIR
                Logger.warning(message=f"RepositoryLocationConfig found raw_base with unexpected type {type(raw_base)}, defaulting to {ret_val}")
        else:
            ret_val = RepositoryLocationConfig._DEFAULT_LOCAL_DIR

        return ret_val

    @staticmethod
    def _parseRemoteURL(unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[URLLocationConfig]:
        ret_val : Optional[URLLocationConfig] = None

        raw_url = RepositoryLocationConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["public_url", "url", "remote_url"],
            to_type=[str, dict],
            default_value=None,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        if raw_url:
            if isinstance(raw_url, str):
                ret_val = URLLocationConfig.FromString(name=f"{schema_name}PublicURL", raw_url=raw_url)
            elif isinstance(raw_url, dict):
                ret_val = URLLocationConfig.FromDict(name=f"{schema_name}PublicURL", unparsed_elements=raw_url)
            else:
                ret_val = RepositoryLocationConfig._DEFAULT_PUBLIC_URL

        return ret_val

    @staticmethod
    def _parseTemplatesURL(unparsed_elements:Map, schema_name:Optional[str]=None) -> URLLocationConfig:
        ret_val : URLLocationConfig

        raw_url = RepositoryLocationConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["templates_url", "templates_base", "url"],
            to_type=[str, dict],
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )
        if raw_url:
            if isinstance(raw_url, str):
                ret_val = URLLocationConfig.FromString(name=f"{schema_name}TemplatesURL", raw_url=raw_url)
            elif isinstance(raw_url, dict):
                ret_val = URLLocationConfig.FromDict(name=f"{schema_name}TemplatesURL", unparsed_elements=raw_url)
            else:
                ret_val = RepositoryLocationConfig._DEFAULT_TEMPLATE_URL
                Logger.warning(message=f"RepositoryLocationConfig found raw templates url with unexpected type {type(raw_url)}, defaulting to {ret_val}")
        else:
            ret_val = RepositoryLocationConfig._DEFAULT_TEMPLATE_URL

        return ret_val

    # *** PRIVATE METHODS ***

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

    _DEFAULT_LOCAL_DIR  : Final[DirectoryLocationConfig] = RepositoryLocationConfig._DEFAULT_LOCAL_DIR
    _DEFAULT_PUBLIC_URL : Final[URLLocationConfig]       = RepositoryLocationConfig._DEFAULT_PUBLIC_URL
    _DEFAULT_DATASETS   : Final[Dict[str, DatasetCollectionSchema]] = {}

    def __init__(self, name:str,
                 # params for class
                 local_directory:Optional[DirectoryLocationConfig | Map | Path | str],
                 public_url:Optional[URLLocationConfig | str],
                 datasets:Optional[Dict[str, DatasetCollectionSchema]],
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        fallbacks : Map = other_elements or {}

        self._indexing : RepositoryLocationConfig           = self._toIndexingConfig(local_directory=local_directory, public_url=public_url, fallbacks=fallbacks, schema_name=name)
        self._datasets : Dict[str, DatasetCollectionSchema] = datasets if datasets is not None else self._parseDatasets(unparsed_elements=fallbacks, schema_name=name)
        super().__init__(name=name, store_type="Repository", other_elements=other_elements)

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def LocalDirectory(self) -> Optional[DirectoryLocationConfig]:
        """Property for the base 'path' to a set of dataset files.

        :return: _description_
        :rtype: Optional[str]
        """
        return self.Indexing.LocalDirectory

    @property
    def PublicURL(self) -> Optional[URLLocationConfig]:
        """The public-facing URL at which this repository can be accessed.
        If the repository is not meant for public access, as is the case for local exports, this property returns None.

        :return: The public-facing URL at which this repository can be accessed, if any.
        :rtype: Optional[str]
        """
        return self.Indexing.PublicURL

    @property
    def IsRemote(self) -> bool:
        return self.PublicURL is not None and self.LocalDirectory is None

    @property
    def TemplatesBase(self) -> URLLocationConfig:
        return self.Indexing.TemplatesURL

    @property
    def Indexing(self) -> RepositoryLocationConfig:
        return self._indexing

    @property
    def Games(self) -> Dict[str, DatasetCollectionSchema]:
        return self._datasets

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @property
    def AsDict(self) -> JSONMap:
        return {
            "CONFIG":self.Indexing.AsDict,
            "datasets":{ key:val.AsDict for key,val in self.Games.items() }
        }

    @property
    def Location(self) -> BaseLocation:
        return self.LocalDirectory if self.LocalDirectory is not None else \
               self.PublicURL      if self.PublicURL      is not None else \
               RepositoryLocationConfig._DEFAULT_LOCAL_DIR

    @property
    def Credential(self) -> EmptyCredential:
        return EmptyCredential.Default()

    @property
    def AsConnectionInfo(self) -> str:
        return f"{self.Name} : {self.Location.Location}"

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DatasetRepositoryConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetRepositoryConfig
        """
        return DatasetRepositoryConfig(name=name, local_directory=None, public_url=None, datasets=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetRepositoryConfig":
        return DatasetRepositoryConfig(
            name="DefaultDatasetRepositoryConfig",
            local_directory=cls._DEFAULT_LOCAL_DIR,
            public_url=cls._DEFAULT_PUBLIC_URL,
            datasets=cls._DEFAULT_DATASETS,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toIndexingConfig(local_directory:Optional[DirectoryLocationConfig | Map | Path | str],
                          public_url:Optional[URLLocationConfig | str],
                          fallbacks:Map, schema_name:Optional[str]=None) -> RepositoryLocationConfig:
        ret_val : RepositoryLocationConfig
        if local_directory is not None or public_url is not None:
            ret_val = RepositoryLocationConfig(name=f"{schema_name}Location", local_dir=local_directory, public_url=public_url, templates_url=None)
        else:
            ret_val = DatasetRepositoryConfig._parseIndexingConfig(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _parseIndexingConfig(unparsed_elements:Map, schema_name:Optional[str]=None) -> RepositoryLocationConfig:
        ret_val : RepositoryLocationConfig

        raw_config = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["CONFIG", "INDEXING", "FILE_INDEXING"],
            to_type=dict,
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )
        ret_val = RepositoryLocationConfig.FromDict(name=f"{schema_name}Index", unparsed_elements=raw_config)

        return ret_val

    @staticmethod
    def _parseDatasets(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, DatasetCollectionSchema]:
        ret_val : Dict[str, DatasetCollectionSchema]

        _data_elems = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["datasets"],
            to_type=[dict, str],
            default_value=None,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True # "optional" because we will look for datasets in raw unparsed_elements if we don't find a separate one here.
        )
        if isinstance(_data_elems, dict):
            ret_val = {
                key : DatasetCollectionSchema.FromDict(name=key, unparsed_elements=datasets if isinstance(datasets, dict) else {})
                for key, datasets in _data_elems.items()
            }
        elif isinstance(_data_elems, str):
            try:
                raw_elems = loadJSONFile(_data_elems)
            except FileNotFoundError:
                raw_elems = {}
            except ModuleNotFoundError:
                raw_elems = {}
            finally:
                ret_val = {
                    key : DatasetCollectionSchema.FromDict(name=key, unparsed_elements=val) \
                    for key, val in raw_elems.items()
                }
        elif len(unparsed_elements) > 0:
            ret_val = {
                key : DatasetCollectionSchema.FromDict(name=key, unparsed_elements=datasets if isinstance(datasets, dict) else {})
                for key, datasets in unparsed_elements.items() if key.upper() != "CONFIG"
            }
        else:
            ret_val = DatasetRepositoryConfig._DEFAULT_DATASETS
            Logger.warning(f"{schema_name} file_list.json does not appear to contain any datasets; defaulting to datasets={ret_val}")

        return ret_val

    # *** PRIVATE METHODS ***
