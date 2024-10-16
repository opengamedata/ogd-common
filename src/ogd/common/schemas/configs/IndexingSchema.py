# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class FileIndexingSchema(Schema):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, local_dir:Path, remote_url:Optional[str], templates_url:str, other_elements:Dict[str, Any]={}):
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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]) -> "FileIndexingSchema":
        _local_dir     : Path
        _remote_url    : Optional[str]
        _templates_url : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} base config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "LOCAL_DIR" in all_elements.keys():
            _local_dir = FileIndexingSchema._parseLocalDir(all_elements["LOCAL_DIR"])
        else:
            _local_dir = Path("./data/")
            Logger.Log(f"{name} config does not have a 'LOCAL_DIR' element; defaulting to local_dir={_local_dir}", logging.WARN)
        if "REMOTE_URL" in all_elements.keys():
            _remote_url = FileIndexingSchema._parseRemoteURL(all_elements["REMOTE_URL"])
        else:
            _remote_url = None
            Logger.Log(f"{name} config does not have a 'REMOTE_URL' element; defaulting to remote_url={_remote_url}", logging.WARN)
        if "TEMPLATES_URL" in all_elements.keys():
            _templates_url = FileIndexingSchema._parseTemplatesURL(all_elements["TEMPLATES_URL"])
        else:
            _templates_url = "https://github.com/opengamedata/opengamedata-samples"
            Logger.Log(f"{name} config does not have a 'TEMPLATES_URL' element; defaulting to templates_url={_templates_url}", logging.WARN)

        _used = {"LOCAL_DIR", "REMOTE_URL", "TEMPLATES_URL"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }

        return FileIndexingSchema(name=name, local_dir=_local_dir, remote_url=_remote_url, templates_url=_templates_url, other_elements=_leftovers)


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
