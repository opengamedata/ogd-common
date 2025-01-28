# import standard libraries
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.utils.Logger import Logger


class KeyCredential(CredentialConfig):
    """Dumb struct to contain data pertaining to loading a key credential
    """
    _DEFAULT_PATH = "./"
    _DEFAULT_FILE = "key.txt"

    def __init__(self, name:str, filename:str, path:Path | str, other_elements:Dict[str, Any] | Any):
        super().__init__(name=name, other_elements=other_elements)
        if isinstance(path, str):
            path = Path(path)
        self._path : Path = path
        self._file : str = filename

    @property
    def File(self) -> str:
        return self._file

    @property
    def Folder(self) -> Path:
        """The path to the folder containing the key credential file.

        :return: The path to the folder containing the key credential file.
        :rtype: Path
        """
        return self._path

    @property
    def Filepath(self) -> Path:
        """The full path to the key credential file.

        :return: The full path to the key credential file.
        :rtype: Path
        """
        return self.Folder / self.File

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"Key: {self.Filepath}"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "KeyCredential":
        _file : Optional[str]
        _path : Optional[Path]

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} key credential config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _file = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["FILE", "KEY"],
            to_type=cls._parseFile,
            default_value=cls._DEFAULT_FILE
        )
        _path = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["PATH"],
            to_type=cls._parsePath,
            default_value=cls._DEFAULT_PATH
        )
        # if we didn't find a PATH, but the FILE has a '/' in it,
        # we should be able to get file separate from path.
        if _path is None and _file is not None and "/" in _file:
            _full_path = Path(_file)
            _path = _full_path.parent
            _file = _full_path.name

        _used = {"FILE", "KEY", "PATH"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return KeyCredential(name=name, filename=_file, path=_path, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "KeyCredential":
        return KeyCredential(
            name="DefaultKeyCredential",
            filename=cls._DEFAULT_FILE,
            path=cls._DEFAULT_PATH,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFile(file) -> str:
        ret_val : Optional[str]
        if isinstance(file, str):
            ret_val = file
        else:
            ret_val = str(file)
            Logger.Log(f"Filename for key credential was unexpected type {type(file)}, defaulting to str(file)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePath(folder) -> Path:
        ret_val : Path
        if isinstance(folder, Path):
            ret_val = folder
        if isinstance(folder, str):
            ret_val = Path(folder)
        else:
            ret_val = Path(str(folder))
            Logger.Log(f"Folder for key credential was unexpected type {type(folder)}, defaulting to Path(str(folder))={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
