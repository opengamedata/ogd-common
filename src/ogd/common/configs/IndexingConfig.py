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
    _DEFAULT_REMOTE_URL = "https://fieldday-web.ad.education.wisc.edu/opengamedata/"
    _DEFAULT_TEMPLATE_URL  = "https://github.com/opengamedata/opengamedata-samples"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, local_dir:Path, remote_url:Optional[str], templates_url:str, other_elements:Optional[Map]=None):
        self._local_dir     : Path          = local_dir
        self._remote_url    : Optional[str] = remote_url
        self._templates_url : str           = templates_url
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
            name            = "DefaultFileIndexingSchema",
            local_dir       = cls._DEFAULT_LOCAL_DIR,
            remote_url      = cls._DEFAULT_REMOTE_URL,
            templates_url   = cls._DEFAULT_TEMPLATE_URL,
            other_elements  = {}
        )

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "FileIndexingConfig":
        _local_dir     : Path
        _remote_url    : Optional[str]
        _templates_url : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} indexing config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _local_dir = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["LOCAL_DIR"],
            parser_function=cls._parseLocalDir,
            default_value=FileIndexingConfig._DEFAULT_LOCAL_DIR
        )
        _remote_url = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["REMOTE_URL"],
            parser_function=cls._parseRemoteURL,
            default_value=FileIndexingConfig._DEFAULT_REMOTE_URL
        )
        _templates_url = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["TEMPLATES_URL"],
            parser_function=cls._parseTemplatesURL,
            default_value=FileIndexingConfig._DEFAULT_TEMPLATE_URL
        )

        _used = {"LOCAL_DIR", "REMOTE_URL", "TEMPLATES_URL"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
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
    def _parseLocalDir(dir) -> Path:
        ret_val : Path
        if isinstance(dir, Path):
            ret_val = dir
        elif isinstance(dir, str):
            ret_val = Path(dir)
        else:
            ret_val = Path(str(dir))
            Logger.Log(f"File Indexing local data directory was unexpected type {type(dir)}, defaulting to Path(str(dir))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseRemoteURL(url) -> str:
        ret_val : str
        if isinstance(url, str):
            ret_val = url
        else:
            ret_val = str(url)
            Logger.Log(f"File indexing remote url was unexpected type {type(url)}, defaulting to str(url)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTemplatesURL(url) -> str:
        ret_val : str
        if isinstance(url, str):
            ret_val = url
        else:
            ret_val = str(url)
            Logger.Log(f"File indexing remote url was unexpected type {type(url)}, defaulting to str(url)={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
