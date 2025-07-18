# standard imports
from pathlib import Path
from typing import Any, Dict, Optional, TypeAlias

# ogd imports
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.EmptyCredential import EmptyCredential
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.utils.typing import Map

FolderCredential : TypeAlias = PasswordCredential | EmptyCredential

# Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.
class DatasetRepositoryConfig(DataStoreConfig):
    """Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.

    This is a separate class from DatasetCollectionSchema because this config exists as its own sub-element of a `file_list.json` file.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_FILE_BASE = "https://opengamedata.fielddaylab.wisc.edu"
    _DEFAULT_TEMPLATE_BASE = "https://github.com/opengamedata/opengamedata-samples"

    def __init__(self, name:str,
                 # params for class
                 location:FileLocationSchema, credential:FolderCredential,
                 file_base_path:Optional[str | Path], template_base_path:Optional[str | Path],
                 # params for parent
                 store_type:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._location       : FileLocationSchema = location   or self._parseLocation(unparsed_elements=unparsed_elements)
        self._credential     : FolderCredential   = credential or self._parseCredential(unparsed_elements=unparsed_elements)
        self._files_base     : Optional[str | Path] = file_base_path     or self._parseFilesBase(unparsed_elements=unparsed_elements)
        self._templates_base : Optional[str | Path] = template_base_path or self._parseTemplatesBase(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def FilesBase(self) -> Optional[str | Path]:
        """Property for the base 'path' to a set of dataset files.
        May be an actual path, or a base URL for accessing from a file server.

        :return: _description_
        :rtype: Optional[str]
        """
        return self._files_base
    @property
    def TemplatesBase(self) -> Optional[str | Path]:
        return self._templates_base

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @property
    def Location(self) -> LocationSchema:
        pass

    @property
    def Credential(self) -> EmptyCredential:
        pass

    @property
    def AsConnectionInfo(self) -> str:
        pass

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "DatasetRepositoryConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetRepositoryConfig
        """
        _files_base     : Optional[str] = cls._parseFilesBase(unparsed_elements=unparsed_elements)
        _templates_base : Optional[str] = cls._parseTemplatesBase(unparsed_elements=unparsed_elements)

        _used = {"files_base", "templates_base"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return DatasetRepositoryConfig(name=name, file_base_path=_files_base, template_base_path=_templates_base, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetRepositoryConfig":
        return DatasetRepositoryConfig(
            name="CONFIG NOT FOUND",
            file_base_path=cls._DEFAULT_FILE_BASE,
            template_base_path=cls._DEFAULT_TEMPLATE_BASE,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFilesBase(unparsed_elements:Map) -> str:
        # The files base is meant to be in a CONFIG sub-dict, so attempt to get it.
        config_elems = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["CONFIG"],
            to_type=Dict,
            default_value=None,
            remove_target=False
        ) or unparsed_elements
        return DatasetRepositoryConfig.ParseElement(
            unparsed_elements=config_elems,
            valid_keys=["files_base"],
            to_type=str,
            default_value=DatasetRepositoryConfig._DEFAULT_FILE_BASE,
            remove_target=True
        )

    @staticmethod
    def _parseTemplatesBase(unparsed_elements:Map) -> str:
        # The files base is meant to be in a CONFIG sub-dict, so attempt to get it.
        # Else, fall back on searching the main thing.
        config_elems = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["CONFIG"],
            to_type=Dict,
            default_value=None,
            remove_target=False
        ) or unparsed_elements
        return DatasetRepositoryConfig.ParseElement(
            unparsed_elements=config_elems,
            valid_keys=["templates_base"],
            to_type=str,
            default_value=DatasetRepositoryConfig._DEFAULT_TEMPLATE_BASE,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
