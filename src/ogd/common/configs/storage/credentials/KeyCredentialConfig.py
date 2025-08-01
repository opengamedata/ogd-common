# import standard libraries
from pathlib import Path
from typing import Dict, Optional, Self
# import local files
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class KeyCredential(CredentialConfig):
    """Dumb struct to contain data pertaining to loading a key credential
    """
    _DEFAULT_PATH = Path("./")
    _DEFAULT_FILE = "key.txt"
    _DEFAULT_LOCATION = FileLocationSchema(
        name="KeyCredentialDefaultLocation",
        folder_path=_DEFAULT_PATH,
        filename=_DEFAULT_FILE,
        other_elements=None
    )

    def __init__(self, name:str, location:Optional[FileLocationSchema], other_elements:Optional[Map]=None):
        """Constructor for the `KeyCredentialConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "KEY" : "key.txt",
            "PATH" : "./"
        },
        ```

        :param name: _description_
        :type name: str
        :param location: _description_
        :type location: Optional[FileLocationSchema]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._location : FileLocationSchema = location or self._parseLocation(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=unparsed_elements)

    @property
    def Filename(self) -> str:
        return self._location.Filename

    @property
    def Folder(self) -> Path:
        """The path to the folder containing the key credential file.

        :return: The path to the folder containing the key credential file.
        :rtype: Path
        """
        return self._location.Folder

    @property
    def Filepath(self) -> Path:
        """The full path to the key credential file.

        :return: The full path to the key credential file.
        :rtype: Path
        """
        return self._location.Filepath

    @property
    def Key(self) -> Optional[str]:
        """The actual key, loaded from the file

        This property loads from the file whenever invoked,
        just to minimize the degree to which keys stick around in the code.

        :return: The full path to the key credential file.
        :rtype: Path
        """
        ret_val  : Optional[str] = None
        try:
            with open(self.Filepath) as keyfile:
                try:
                    ret_val = keyfile.read()
                except IOError:
                    Logger.Log(f"Could not read key file at {self.Filepath}, an I/O error occurred!")
        except FileNotFoundError:
            Logger.Log(f"Could not open key file {self.Filepath}, the file does not exist!")
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"Key: {self.Filepath}"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "KeyCredential":
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
        return KeyCredential(name=name, location=None, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "KeyCredential":
        return KeyCredential(
            name="DefaultKeyCredential",
            location=cls._DEFAULT_LOCATION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseLocation(unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None) -> FileLocationSchema:
        default_overrides : Dict[str, str] = {"file" : "key"}
        final_overrides   : Dict[str, str] = default_overrides | (key_overrides or {})

        return FileLocationSchema.FromDict(name="KeyCredentialLocation", unparsed_elements=unparsed_elements, key_overrides=final_overrides)

    # *** PRIVATE METHODS ***
