# import standard libraries
from pathlib import Path
from typing import Any, Dict, Final, Optional, Self
# import local files
from ogd.common.configs.locations.LocationConfig import LocationConfig
from ogd.common.configs.locations.DirectoryLocationConfig import DirectoryLocationConfig
from ogd.common.configs.locations.URLLocationConfig import URLLocationConfig
from ogd.common.utils.typing import JSONMap, Map
from ogd.common.utils.Logger import Logger

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
        ret_val : Optional[URLLocationConfig]

        raw_url = RepositoryLocationConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["public_url", "url", "remote_url"],
            to_type=[str, dict],
            default_value=None,
            remove_target=True,
            schema_name=schema_name
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
