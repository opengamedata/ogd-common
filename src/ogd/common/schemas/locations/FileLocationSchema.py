## import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class TableStructureSchema
class FileLocationSchema(LocationSchema):
    """Class to encode the location of data within a database resource.

    Generally, the location of a database system would be a URLLocation,
    while DatabaseLocation refers to the location of a specific database or table within such a system.
    """

    _DEFAULT_PATH = Path("./")
    _DEFAULT_FILENAME = "file.tsv"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, folder_path:Path, filename:str, other_elements:Optional[Map]):
        unparsed_elements : Map = other_elements or {}

        self._folder_path  : Path
        self._filename     : str

        # 1. If we got both params, then just use them.
        if folder_path and filename:
            self._folder_path = folder_path
            self._filename    = filename
        # 2. Otherwise, try to get as full path as first try. If it return something, then we've got what we need.
        else:
            parsed_path = self._parsePath(unparsed_elements=unparsed_elements)
            if parsed_path:
                self._folder_path = parsed_path[0]
                self._filename    = parsed_path[1]
        # 3. If there wasn't a full path, then we move on to just parse folder and filename from dict directly.
            else:
                self._folder_path = folder_path or self._parsePath(unparsed_elements=unparsed_elements)
                self._filename    = filename    or self._parseFilename(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def FolderPath(self) -> Path:
        """The path of the folder containing the file located by this schema.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._folder_path

    @property
    def Filename(self) -> str:
        return self._filename

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return str(self.FolderPath / self.Filename)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.FolderPath / self.Filename}"
        return ret_val

    @classmethod
    def Default(cls) -> "FileLocationSchema":
        return FileLocationSchema(
            name="DefaultFileLocation",
            folder_path=cls._DEFAULT_PATH,
            filename=cls._DEFAULT_FILENAME,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "FileLocationSchema":
        """Create a DatabaseLocationSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: GameSourceSchema
        """
        _folder_path : Path
        _filename    : str

        # 2. Otherwise, try to get as full path as first try. If it return something, then we've got what we need.
        parsed_path = cls._parsePath(unparsed_elements=unparsed_elements)
        _used = {"path"}
        if parsed_path:
            _folder_path = parsed_path[0]
            _filename    = parsed_path[1]
        # 3. If there wasn't a full path, then we move on to just parse folder and filename from dict directly.
        else:
            _folder_path = cls._parseFolderPath(unparsed_elements=unparsed_elements)
            _filename    = cls._parseFilename(unparsed_elements=unparsed_elements)
            _used = _used.union({"folder", "filename", "file"})

        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return FileLocationSchema(name=name, folder_path=_folder_path, filename=_filename, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parsePath(unparsed_elements:Map, keys:List[str]=["path"]) -> Optional[Tuple[Path, str]]:
        """Function to parse a full path into a folder and filename

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Optional[str]
        """
        ret_val = None

        raw_path = FileLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=keys,
            to_type=Path,
            default_value=None,
            remove_target=True
        )
        if raw_path:
            ret_val = (raw_path.parent, raw_path.name)
            if not raw_path.is_file():
                Logger.Log(f"FileLocationSchema was given a path '{raw_path}' which is not a valid file!", logging.WARNING)
            elif not "." in raw_path.name:
                Logger.Log(f"FileLocationSchema was given a path '{raw_path}' which does not include a file extension!", logging.WARNING)

        return ret_val

    @staticmethod
    def _parseFolderPath(unparsed_elements:Map, keys:List[str]=["folder"]) -> Path:
        return FileLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=keys,
            to_type=Path,
            default_value=FileLocationSchema._DEFAULT_PATH,
            remove_target=True
        )

    @staticmethod
    def _parseFilename(unparsed_elements:Map, keys:List[str]=["filename", "file"]) -> str:
        return FileLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=keys,
            to_type=str,
            default_value=FileLocationSchema._DEFAULT_FILENAME,
            remove_target=True
        )
