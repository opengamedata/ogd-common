# import standard libraries
import logging
from typing import Any, Dict, Optional, TypeAlias
from pathlib import Path
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.EmptyCredential import EmptyCredential
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

FileCredential : TypeAlias = PasswordCredential | EmptyCredential

class FileStoreConfig(DataStoreConfig):
    _DEFAULT_FOLDER_PATH = Path('./data')
    _DEFAULT_FILE_NAME = "UNKNOWN.tsv"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 folder_path:Path, file_name:str, file_credential:FileCredential,
                 # params for parent
                 store_type:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._folder_path : Path           = folder_path     or self._parseFolder(unparsed_elements=other_elements)
        self._file_name   : str            = file_name       or self._parseFilename(unparsed_elements=unparsed_elements)
        self._credential  : FileCredential = file_credential or self._parseCredential(unparsed_elements=unparsed_elements)
        super().__init__(name=name, store_type=store_type, other_elements=unparsed_elements)

    @property
    def Filename(self) -> str:
        return self._file_name

    @property
    def Folder(self) -> Path:
        """The path to the folder containing the data store file

        :return: The path to the folder containing the data store file.
        :rtype: Path
        """
        return self._folder_path

    @property
    def FileExtension(self) -> str:
        return self._file_name.split(".")[-1]

    @property
    def Filepath(self) -> str | Path:
        return self._folder_path / self.Filename

    @property
    def Location(self) -> str | Path:
        return self.Filepath

    @property
    def Credential(self) -> PasswordCredential | EmptyCredential:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = "FILE SOURCE"
        ret_val = f"{self.Name} : Folder=_{self.Folder}_, File=_{self.Filename}_"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.Name}:{self.Filepath}"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "FileStoreConfig":
        _folder_path : Path
        _file_name   : str

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} File source config, unparsed_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _folder_path = cls._parseFolder(unparsed_elements=unparsed_elements)
        _file_name = cls._parseFilename(unparsed_elements=unparsed_elements)
        _credential = cls._parseCredential(unparsed_elements=unparsed_elements)

        return FileStoreConfig(name=name, folder_path=_folder_path, file_name=_file_name, file_credential=_credential, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "FileStoreConfig":
        return FileStoreConfig(
            name="DefaultFileStoreConfig",
            folder_path=cls._DEFAULT_FOLDER_PATH,
            file_name=cls._DEFAULT_FILE_NAME,
            file_credential=EmptyCredential.Default(),
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFolder(unparsed_elements:Map) -> Path:
        return FileStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PATH"],
            to_type=Path,
            default_value=FileStoreConfig._DEFAULT_FOLDER_PATH,
            remove_target=True
        )

    @staticmethod
    def _parseFilename(unparsed_elements:Map) -> str:
        return FileStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["FILENAME"],
            to_type=str,
            default_value=FileStoreConfig._DEFAULT_FILE_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> FileCredential:
        ret_val : FileCredential
        _cred_elements = FileStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["FILE_CREDENTIAL"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if _cred_elements:
            ret_val = PasswordCredential.FromDict(name="FileStoreCredential", unparsed_elements=_cred_elements)
        else:
            ret_val = EmptyCredential.FromDict(name="FileStoreCredential", unparsed_elements={})
        return ret_val

    # *** PRIVATE METHODS ***
