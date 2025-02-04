# import standard libraries
import logging
from pathlib import Path
from typing import Optional
# import local files
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class KeyCredential(CredentialConfig):
    """Dumb struct to contain data pertaining to loading a key credential
    """
    _DEFAULT_PATH = "./"
    _DEFAULT_FILE = "key.txt"

    def __init__(self, name:str, filename:str, path:Path | str, other_elements:Optional[Map]):
        unparsed_elements : Map = other_elements or {}
        if isinstance(path, str):
            path = Path(path)
        self._path : Path = path     or self._parsePath(unparsed_elements=unparsed_elements)
        self._file : str  = filename or self._parseFilename(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=unparsed_elements)

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
    def FromDict(cls, name:str, unparsed_elements:Map)-> "KeyCredential":
        """Create a Key Credential from a dict.

        Expects dictionary to have the following form:
        ```json
        {
           "FILE" : "key.txt",
           "PATH" : "./"
        }
        ```

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: KeyCredential
        """
        _file : Optional[str]
        _path : Optional[Path]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} key credential config, all_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _file = cls._parseFilename(unparsed_elements=unparsed_elements)
        _path = cls._parsePath(unparsed_elements=unparsed_elements)
        # if we didn't find a PATH, but the FILE has a '/' in it,
        # we should be able to get file separate from path.
        if _path is None and _file is not None and "/" in _file:
            _full_path = Path(_file)
            _path = _full_path.parent
            _file = _full_path.name

        return KeyCredential(name=name, filename=_file, path=_path, other_elements=unparsed_elements)

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
    def _parseFilename(unparsed_elements:Map) -> str:
        return KeyCredential.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["FILE", "KEY"],
            to_type=str,
            default_value=KeyCredential._DEFAULT_FILE,
            remove_target=True
        )

    @staticmethod
    def _parsePath(unparsed_elements:Map) -> Path:
        return KeyCredential.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PATH"],
            to_type=Path,
            default_value=KeyCredential._DEFAULT_PATH,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
