# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.Config import Config
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class FileIndexingConfig(Config):
    _DEFAULT_LOCAL_DIR  = Path("./data/")
    _DEFAULT_REMOTE_URL = "https://opengamedata.fielddaylab.wisc.edu/opengamedata/"
    _DEFAULT_TEMPLATE_URL  = "https://github.com/opengamedata/opengamedata-samples"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, local_dir:Path, remote_url:Optional[str], templates_url:str, other_elements:Optional[Map]=None):
        unparsed_elements : Map = {key.upper() : val for key, val in other_elements.items()} if other_elements else {}

        self._local_dir     : Path          = local_dir     or self._parseLocalDir(unparsed_elements=unparsed_elements)
        self._remote_url    : Optional[str] = remote_url    or self._parseRemoteURL(unparsed_elements=unparsed_elements)
        self._templates_url : str           = templates_url or self._parseTemplatesURL(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def LocalDirectory(self) -> Path:
        return self._local_dir

    @property
    def RemoteURL(self) -> Optional[str]:
        return self._remote_url

    @property
    def TemplatesURL(self) -> str:
        return self._templates_url

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def Default(cls) -> "FileIndexingConfig":
        return FileIndexingConfig(
            name            = "DefaultFileIndexingConfig",
            local_dir       = cls._DEFAULT_LOCAL_DIR,
            remote_url      = cls._DEFAULT_REMOTE_URL,
            templates_url   = cls._DEFAULT_TEMPLATE_URL,
            other_elements  = {}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "FileIndexingConfig":
        """Create a file indexing Configuration from a dict.

        Expects dictionary to have the following form:
        ```json
        {
            "LOCAL_DIR"     : "./data/",
            "REMOTE_URL"    : "https://opengamedata.fielddaylab.wisc.edu/",
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
        _local_dir     : Path          = cls._parseLocalDir(unparsed_elements=unparsed_elements)
        _remote_url    : Optional[str] = cls._parseRemoteURL(unparsed_elements=unparsed_elements)
        _templates_url : str           = cls._parseTemplatesURL(unparsed_elements=unparsed_elements)

        _used = {"LOCAL_DIR", "REMOTE_URL", "TEMPLATES_URL"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return FileIndexingConfig(name=name, local_dir=_local_dir, remote_url=_remote_url, templates_url=_templates_url, other_elements=_leftovers)


    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name} : Local=_{self.LocalDirectory}_, Remote=_{self.RemoteURL}_"
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseLocalDir(unparsed_elements:Map) -> Path:
        return FileIndexingConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["LOCAL_DIR"],
            to_type=Path,
            default_value=FileIndexingConfig._DEFAULT_LOCAL_DIR,
            remove_target=True
        )

    @staticmethod
    def _parseRemoteURL(unparsed_elements:Map) -> str:
        return FileIndexingConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["REMOTE_URL"],
            to_type=str,
            default_value=FileIndexingConfig._DEFAULT_REMOTE_URL,
            remove_target=True
        )

    @staticmethod
    def _parseTemplatesURL(unparsed_elements:Map) -> str:
        return FileIndexingConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["TEMPLATES_URL"],
            to_type=str,
            default_value=FileIndexingConfig._DEFAULT_TEMPLATE_URL,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
