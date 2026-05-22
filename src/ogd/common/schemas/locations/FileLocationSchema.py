## import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Self, Tuple
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import JSONMap, Map

## @class FileLocationSchema
class FileLocationSchema(LocationSchema):
    """Class to encode the location of data within a database resource.

    Generally, the location of a database system would be a URLLocation,
    while DatabaseLocation refers to the location of a specific database or table within such a system.
    """

    _DEFAULT_PATH     : Final[Path] = Path("./file.tsv")
    _DEFAULT_FILENAME : Final[None] = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, folder_path:Optional[Path | str], filename:Optional[str], other_elements:Optional[Map]=None):
        """Constructor for the `FileLocationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "folder" : "path/to/folder",
            "filename" : "file.ext"
        },
        ```

        Supports "path" in place of "folder", and "file" in place of "filename."
        Supports cases where the folder path includes the file, though this is not the standard use of the schema.

        :param name: _description_
        :type name: str
        :param folder_path: A path to the folder containing the desired file.
                            Optionally, the file may be included in this path, though it is preferable to pass in the filename separately.
        :type folder_path: Path | str
        :param filename: The name of the desired file within the `folder_path`.
        :type filename: str
        :param other_elements: A dictionary in which to search for any elements not given as arguments, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._folder_path  : Path
        self._filename     : str

        raw_path  = self._getFolderPath(raw_val=folder_path, unparsed_elements=unparsed_elements, schema_name=name)
        raw_filename = self._getFilename(raw_val=filename, unparsed_elements=unparsed_elements, schema_name=name)

        # If raw_path pointed at a file, we use parent folder for the path, and 'name' for the filename...
        if raw_path.is_file():
            self._folder_path = raw_path.parent
            if raw_filename is None:
                self._filename = raw_path.name
        else:
            self._folder_path = raw_path
        # unless raw filename also came up with something. Then we use raw filename for file name, even if raw path pointed at a file.
        # Always choose to use the more specific parameter.
        if raw_filename is not None:
            self._filename = raw_filename
            if raw_path.is_file():
                Logger.Log("FileLocationSchema was given a folder path that included a file, and a filename! Defaulting to the given filename, in place of the file contained in the folder path.", logging.WARNING)
        

        super().__init__(name=name, other_elements=other_elements)

    @property
    def Folder(self) -> Path:
        """The path of the folder containing the file located by this schema.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._folder_path

    @property
    def Filename(self) -> str:
        """The name of the file indicated by the FileLocationSchema

        :return: _description_
        :rtype: str
        """
        return self._filename

    @property
    def Filepath(self) -> Path:
        """The full path to the file indicated by the FileLocationSchema

        :return: _description_
        :rtype: Path
        """
        return self.Folder / self.Filename

    @property
    def FileExists(self):
        return self.Filepath.is_file()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return str(self.Filepath)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.Folder / self.Filename}"
        return ret_val

    @property
    def AsDict(self) -> JSONMap:
        return {
            "folder":str(self.Folder),
            "filename":self.Filename
        }

    @classmethod
    def Default(cls) -> "FileLocationSchema":
        return FileLocationSchema(
            name="DefaultFileLocation",
            folder_path=cls._DEFAULT_PATH,
            filename=cls._DEFAULT_FILENAME,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "FileLocationSchema":
        """Create a DatabaseLocationSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :param key_overrides: _description_, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :param default_override: _description_, defaults to None
        :type default_override: Optional[Self], optional
        :return: _description_
        :rtype: FileLocationSchema
        """
        # Call the 'get' functions with overrides, and pass along result as values for the constructor.
        # It will still handle the sorting out of what is file and what is path.
        _folder_path : Path          = cls._getFolderPath(raw_val=None, unparsed_elements=unparsed_elements, schema_name=name, key_overrides=key_overrides, default_override=default_override)
        _filename    : Optional[str] = cls._getFilename(raw_val=None, unparsed_elements=unparsed_elements, schema_name=name, key_overrides=key_overrides, default_override=default_override)
        _used = {"folder", "filename", "path", "file"}

        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return FileLocationSchema(name=name, folder_path=_folder_path, filename=_filename, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    @staticmethod
    def FromPath(name:str, fullpath:Path | str) -> "FileLocationSchema":
        if isinstance(fullpath, str):
            fullpath = Path(fullpath)
        if fullpath:
            if not "." in fullpath.name:
                Logger.Log(f"FileLocationSchema was given a path '{fullpath}' which does not include a file extension!", logging.WARNING)
            return FileLocationSchema(name=name, folder_path=fullpath.parent, filename=fullpath.name)

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _getFolderPath(raw_val:Any, unparsed_elements:Map,
                         schema_name:Optional[str]=None,
                         key_overrides:Optional[Dict[str, str]]=None,
                         default_override:Optional["FileLocationSchema"]=None) -> Path:
        default_keys : List[str] = ["folder", "path"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_value : Path = default_override.Folder if default_override else FileLocationSchema._DEFAULT_PATH

        return FileLocationSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=Path,
            default_value=default_value,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _getFilename(raw_val:Any, unparsed_elements:Map,
                       schema_name:Optional[str]=None,
                       key_overrides:Optional[Dict[str, str]]=None,
                       default_override:Optional["FileLocationSchema"]=None) -> Optional[str]:
        default_keys  : List[str] = ["filename", "file"]
        search_keys   : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_value : Optional[str] = default_override.Filename if default_override else FileLocationSchema._DEFAULT_FILENAME

        return FileLocationSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_value,
            remove_target=True,
            optional_element=True,
            schema_name=schema_name
        )
