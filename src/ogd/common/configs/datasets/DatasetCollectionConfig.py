# standard imports
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# ogd imports
from ogd.common.configs.Config import Config
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

# Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.
class DatasetRepositoryConfig(Config):
    """Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.

    This is a separate class from DatasetCollectionSchema because this config exists as its own sub-element of a `file_list.json` file.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_FILE_BASE = "https://fieldday-web.ad.education.wisc.edu/opengamedata/"
    _DEFAULT_TEMPLATE_BASE = "https://github.com/opengamedata/opengamedata-samples"

    def __init__(self, name:str, file_base_path:Optional[str | Path], template_base_path:Optional[str | Path], other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}

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

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "DatasetRepositoryConfig":
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
        return DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["files_base"],
            to_type=str,
            default_value=DatasetRepositoryConfig._DEFAULT_FILE_BASE,
            remove_target=True
        )

    @staticmethod
    def _parseTemplatesBase(unparsed_elements:Map) -> str:
        return DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["templates_base"],
            to_type=str,
            default_value=DatasetRepositoryConfig._DEFAULT_TEMPLATE_BASE,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
