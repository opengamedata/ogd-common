# standard imports
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Optional, Self, TypeAlias

# ogd imports
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.schemas.locations.DirectoryLocationSchema import DirectoryLocationSchema
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.utils.typing import Map

BaseLocation : TypeAlias = URLLocationSchema | DirectoryLocationSchema

# Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.
class LocalDatasetRepositoryConfig(DatasetRepositoryConfig):

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_FILE_BASE = DirectoryLocationSchema(
        name="DefaultRepositoryLocation",
        folder_path=Path("./data"),
        other_elements=None
    )
    _DEFAULT_TEMPLATE_BASE = URLLocationSchema(
        name="DefaultTemplatesBase",
        url=urlparse("https://github.com/opengamedata/opengamedata-samples"),
        other_elements=None
    )
    _DEFAULT_DATASETS = {}

    def __init__(self, name:str,
                 # params for class
                 files_base:Optional[DirectoryLocationSchema],
                 templates_base:Optional[BaseLocation],
                 datasets:Optional[Dict[str, DatasetCollectionSchema]],
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        _files_base      : DirectoryLocationSchema = files_base or self._parseFilesBase(unparsed_elements=unparsed_elements)
        super().__init__(name=name, files_base=self._files_base, templates_base=templates_base, datasets=datasets, other_elements=other_elements)
        self._files_base : DirectoryLocationSchema = _files_base

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def FilesBase(self) -> DirectoryLocationSchema:
        """Property for the base 'path' to a set of dataset files.
        May be an actual path, or a base URL for accessing from a file server.

        :return: _description_
        :rtype: Optional[str]
        """
        return self._files_base

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DatasetRepositoryConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetRepositoryConfig
        """
        return LocalDatasetRepositoryConfig(name=name, files_base=None, templates_base=None, datasets=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFilesBase(unparsed_elements:Map) -> DirectoryLocationSchema:
        ret_val : DirectoryLocationSchema

        raw_base = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["files_base"],
            to_type=str,
            default_value=None,
            remove_target=True
        )
        if raw_base:
            ret_val = DirectoryLocationSchema(name="RepositoryFilesBase", folder_path=Path(raw_base))
        else:
            ret_val = DatasetRepositoryConfig._DEFAULT_FILE_BASE

        return ret_val

    # *** PRIVATE METHODS ***
