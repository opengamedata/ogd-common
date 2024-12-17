# import standard libraries
import logging
from typing import Any, Dict, Optional
from pathlib import Path
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.utils.Logger import Logger

class FileStoreConfig(DataStoreConfig):
    _DEFAULT_FOLDER_PATH = Path('./data')
    _DEFAULT_FILE_NAME = "UNKNOWN.tsv"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, folder_path:Path, file_name:str, other_elements:Dict[str, Any]):
        self._folder_path : Path = folder_path
        self._file_name   : str  = file_name
        super().__init__(name=name, other_elements=other_elements)

    @property
    def FilePath(self) -> Path:
        return self._folder_path / self.FileName

    @property
    def FolderPath(self) -> Path:
        return self._folder_path

    @property
    def FileName(self) -> str:
        return self._file_name

    @property
    def FileExtension(self) -> str:
        return self._file_name.split(".")[-1]

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"FILE SOURCE"
        ret_val = f"{self.Name} : Folder=_{self.FolderPath}_, File=_{self.FileName}_"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self._name}"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "FileStoreConfig":
        _folder_path : Path
        _file_name   : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} File source config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _folder_path = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["PATH"],
            parser_function=cls._parseFolder,
            default_value=FileStoreConfig._DEFAULT_FOLDER_PATH
        )
        _file_name = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["FILENAME"],
            parser_function=cls._parseFilename,
            default_value=FileStoreConfig._DEFAULT_FILE_NAME
        )

        _used = {"PATH", "FILENAME"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return FileStoreConfig(name=name, folder_path=_folder_path, file_name=_file_name, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "FileStoreConfig":
        return FileStoreConfig(
            name="DefaultFileSourceSchema",
            folder_path=cls._DEFAULT_FOLDER_PATH,
            file_name=cls._DEFAULT_FILE_NAME,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFolder(dir) -> Path:
        ret_val : Path
        if isinstance(dir, Path):
            ret_val = dir
        elif isinstance(dir, str):
            ret_val = Path(dir)
        else:
            ret_val = Path(str(dir))
            Logger.Log(f"File Source folder directory was unexpected type {type(dir)}, defaulting to Path(str(dir))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseFilename(fname) -> str:
        ret_val : str
        if isinstance(fname, str):
            ret_val = fname
        else:
            ret_val = str(fname)
            Logger.Log(f"File source name was unexpected type {type(fname)}, defaulting to str(fname)={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
