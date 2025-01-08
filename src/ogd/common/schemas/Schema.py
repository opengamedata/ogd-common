# import standard libraries
import abc
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
# import local files
from ogd.common import schemas
from ogd.common.utils import fileio
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class Schema(abc.ABC):

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def AsMarkdown(self) -> str:
        """Gets a markdown-formatted representation of the schema.

        :return: A markdown-formatted representation of the schema.
        :rtype: str
        """
        pass

    @classmethod
    @abc.abstractmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "Schema":
        """_summary_

        TODO : Make classmethod, slightly simplifies how we access default values

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: _description_
        :rtype: Schema
        """
        pass

    @classmethod
    @abc.abstractmethod
    def Default(cls) -> "Schema":
        """Property to get an instance of the Schema with default member values.

        Note that these defaults may or may not be a usable configuration.
        :return: A schema with default member values.
        :rtype: Self
        """
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, other_elements:Optional[Map]=None):
        self._name : str
        self._other_elements : Map

        self._name = Schema._parseName(name)

        self._other_elements = other_elements or {}
        if len(self._other_elements.keys()) > 0:
            Logger.Log(f"Schema for {self.Name} contained nonstandard elements {self.NonStandardElementNames}")

    def __str__(self):
        return f"{type(self).__name__}[{self.Name}]"

    def __repr__(self):
        return f"{type(self).__name__}[{self.Name}]"

    @property
    def Name(self) -> str:
        """Gets the name of the specific schema represented by the class instance.

        :return: The name of the specific schema represented by the class instance.
        :rtype: str
        """
        return self._name

    @property
    def NonStandardElements(self) -> Dict[str, Any]:
        """Gets a sub-dictionary of any non-standard schema elements found in the source dictionary for the given schema instance.

        :return: A dictionary of any non-standard schema elements found in the source dictionary for the given schema instance.
        :rtype: Dict[str, Any]
        """
        return self._other_elements

    @property
    def NonStandardElementNames(self) -> List[str]:
        """Gets a list of names of non-standard schema elements found in the source dictionary for the given schema instance.

        :return: A list of names of non-standard schema elements found in the source dictionary for the given schema instance.
        :rtype: List[str]
        """
        return list(self._other_elements.keys())

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, schema_name:str, schema_path:Path = Path(schemas.__file__).parent / "table_schemas/") -> "Schema":
        _table_format_name : str = schema_name

        if not _table_format_name.lower().endswith(".json"):
            _table_format_name += ".json"
        _schema = fileio.loadJSONFile(filename=_table_format_name, path=schema_path)

        return cls.FromDict(name=schema_name, all_elements=_schema)

    @classmethod
    def ElementFromDict(cls, all_elements:Dict[str, Any], element_names:List[str], parser_function:Callable, default_value:Any, logger:Optional[logging.Logger]=None) -> Any:
        """_summary_

        TODO : Redo this concept in a way that we can still get type safety by directly calling parse functions in individual schema classes.

        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param element_names: _description_
        :type element_names: List[str]
        :param parser_function: _description_
        :type parser_function: Callable
        :param default_value: _description_
        :type default_value: Any
        :param logger: _description_, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: _description_
        :rtype: Any
        """
        for name in element_names:
            if name in all_elements:
                return parser_function(all_elements[name])
        _msg = f"{cls.__name__} config does not have a '{element_names[0]}' element; defaulting to {element_names[0]}={default_value}"
        logger.warning(_msg) if logger else Logger.Log(_msg, logging.WARN)
        return default_value

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseName(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Schema name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
