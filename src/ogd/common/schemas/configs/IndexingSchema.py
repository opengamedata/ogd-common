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

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]) -> "FileIndexingSchema":
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
        _local_dir = FileIndexingSchema.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["LOCAL_DIR"],
            parser_function=FileIndexingSchema._parseLocalDir,
            default_value=Path("./data/")
        )
        _remote_url = FileIndexingSchema.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["REMOTE_URL"],
            parser_function=FileIndexingSchema._parseRemoteURL,
            default_value=None
        )
        _templates_url = FileIndexingSchema.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["TEMPLATES_URL"],
            parser_function=FileIndexingSchema._parseTemplatesURL,
            default_value="https://github.com/opengamedata/opengamedata-samples"
        )

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
