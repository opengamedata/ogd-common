## import standard libraries
from pathlib import Path
from typing import Dict, List, Optional, Self
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.typing import Map

## @class TableStructureSchema
class DirectoryLocationSchema(LocationSchema):
    """Class to encode the location of data within a database resource.

    Generally, the location of a database system would be a URLLocation,
    while DatabaseLocation refers to the location of a specific database or table within such a system.
    """

    _DEFAULT_PATH = Path("./")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, folder_path:Optional[Path], other_elements:Optional[Map]=None):
        """Constructor for the `DirectoryLocationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "folder": "path/to/folder"
        },
        ```

        :param name: _description_
        :type name: str
        :param folder_path: _description_
        :type folder_path: Optional[Path]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._folder_path = folder_path or self._parseFolderPath(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def FolderPath(self) -> Path:
        """The path of the folder containing the file located by this schema.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._folder_path

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return str(self.FolderPath)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.FolderPath}"
        return ret_val

    @classmethod
    def Default(cls) -> "DirectoryLocationSchema":
        return DirectoryLocationSchema(
            name="DefaultFolderLocation",
            folder_path=cls._DEFAULT_PATH,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DirectoryLocationSchema":
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
        _folder_path = cls._parseFolderPath(unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)
        return DirectoryLocationSchema(name=name, folder_path=_folder_path, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFolderPath(unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional["DirectoryLocationSchema"]=None) -> Path:
        default_keys : List[str] = ["folder", "path"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_value : Path = default_override.FolderPath if default_override else DirectoryLocationSchema._DEFAULT_PATH

        return DirectoryLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=Path,
            default_value=default_value,
            remove_target=True
        )
