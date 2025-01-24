# import standard libraries
import abc
import builtins
import logging
import datetime
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List, Optional, Type
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

        self._name = Schema._parseString(name="DefaultSchemaName", value=name)

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
    def FromFile(cls, schema_name:str, schema_path:Path, search_templates:bool=False):
        return cls._fromFile(schema_name=schema_name, schema_path=schema_path)

    @classmethod
    def ParseElement(cls, all_elements:Dict[str, Any], valid_keys:List[str], value_type:Type, default_value:Any) -> Any:
        """Function to parse an individual element from a dictionary, given a list of possible keys for the element, and a desired type.

        :param all_elements: A dictionary containing all elements to search through
        :type all_elements: Dict[str, Any]
        :param valid_keys: A list of which keys to search for to find the desired element. This function will choose they first key in the list that appears in the `all_elements` dictionary.
        :type valid_keys: List[str]
        :param value_type: The desired type of value to return
        :type value_type: Type
        :param default_value: A default value to return, if a valid value could not be parsed.
        :type default_value: Any
        :return: The targeted value, with given type; otherwise the given default value.
        :rtype: Any
        """
        for name in valid_keys:
            if name in all_elements:
                value = all_elements[name]
                match (value_type):
                    case builtins.int:
                        return Schema._parseInt(name=name, value=value)
                    case builtins.float:
                        return Schema._parseFloat(name=name, value=value)
                    case builtins.str:
                        return Schema._parseString(name=name, value=value)
                    case datetime.date:
                        return Schema._parseDate()
                    case datetime.datetime:
                        return Schema._parseDatetime()
                    case datetime.timedelta:
                        return Schema._parseTimedelta()
                    case _:
                        _msg = f"Requested type of {value_type} for '{valid_keys[0]}' is unknown; defaulting to {valid_keys[0]}={default_value}"
                        Logger.Log(_msg, logging.WARN)
                        return default_value
        _msg = f"{cls.__name__} config does not have a '{valid_keys[0]}' element; defaulting to {valid_keys[0]}={default_value}"
        Logger.Log(_msg, logging.WARN)
        return default_value

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @classmethod
    def _fromFile(cls, schema_name:str, schema_path:Path, search_templates:bool=False):
        ret_val : Schema
        _formatted_name : str = schema_name

        # 1. make sure the name and path are in the right form.
        if not _formatted_name.lower().endswith(".json"):
            _formatted_name += ".json"
        # 2. try to actually load the contents of the file.
        try:
            schema_contents = fileio.loadJSONFile(filename=_formatted_name, path=schema_path)
        except (ModuleNotFoundError, FileNotFoundError) as err:
            # Case 1: Didn't find module, nothing else to try
            if isinstance(err, ModuleNotFoundError):
                Logger.Log(f"Unable to load schema at {schema_path / schema_name}, module ({schema_path}) does not exist! Using default schema instead", logging.ERROR, depth=1)
                ret_val = cls.Default()
            # Case 2a: Didn't find file, search for template
            elif search_templates:
                Logger.Log(f"Unable to load schema at {schema_path / schema_name}, {schema_name} does not exist! Trying to load from json template instead...", logging.WARNING, depth=1)
                ret_val = cls._schemaFromTemplate(schema_path=schema_path, schema_name=schema_name)
            # Case 2b: Didn't find file, don't search for template
            else:
                Logger.Log(f"Unable to load schema at {schema_path / schema_name}, {schema_name} does not exist! Using default schema instead", logging.ERROR, depth=1)
                ret_val = cls.Default()
        else:
            if schema_contents is None:
                Logger.Log(f"Could not load schema at {schema_path / schema_name}, the file was empty! Using default schema instead", logging.ERROR, depth=1)
                ret_val = cls.Default()
            else:
                ret_val = cls.FromDict(name=schema_name, all_elements=schema_contents)

        return ret_val

    @classmethod
    def _schemaFromTemplate(cls, schema_path:Path, schema_name:str) -> "Schema":
        ret_val : Schema

        template_name = schema_name + ".template"
        try:
            template_contents = fileio.loadJSONFile(filename=template_name, path=schema_path, autocorrect_extension=False)
        except FileNotFoundError:
            _msg = f"Unable to load schema template at {schema_path / template_name}, {template_name} does not exist!."
            Logger.Log(_msg, logging.WARN, depth=1)
            print(f"(via print) {_msg}.")
        else:
            if template_contents is not None:
                Logger.Log(f"Successfully loaded {schema_name} from template.", logging.INFO, depth=1)
                Logger.Log(f"Trying to copy {schema_name} from template, for future use...", logging.DEBUG, depth=2)
                template = schema_path / template_name
                try:
                    copyfile(template, schema_path / schema_name)
                except Exception as cp_err:
                    _msg = f"Could not make a copy of {schema_name} from template, a {type(cp_err)} error occurred:\n{cp_err}"
                    Logger.Log(         _msg, logging.WARN, depth=1)
                    print(f"(via print) {_msg}")
                else:
                    Logger.Log(f"Successfully copied {schema_name} from template.", logging.DEBUG, depth=2)
        return cls.FromDict(name=schema_name, all_elements=template_contents)
    
    @classmethod
    def _parseInt(cls, name:str, value:Any) -> int:
        ret_val : int
        if isinstance(value, int):
            ret_val = value
        elif isinstance(value, float):
            ret_val = int(round(value))
            Logger.Log(f"{cls.__name__} element {name} was a float value, rounding to nearest int ({ret_val}).", logging.WARN)
        else:
            ret_val = int(value)
            Logger.Log(f"{cls.__name__} element {name} was unexpected type {type(value)}, defaulting to int(value) == {ret_val}.", logging.WARN)
        return ret_val
    
    @classmethod
    def _parseFloat(cls, name:str, value:Any) -> float:
        ret_val : float
        if isinstance(value, float):
            ret_val = value
        else:
            ret_val = int(value)
            Logger.Log(f"{cls.__name__} element {name} was unexpected type {type(value)}, defaulting to float(value) == {ret_val}.", logging.WARN)
        return ret_val

    @classmethod
    def _parseString(cls, name:str, value:Any) -> str:
        ret_val : str
        if isinstance(value, str):
            ret_val = value
        else:
            ret_val = str(value)
            Logger.Log(f"{cls.__name__} element {name} was unexpected type {type(value)}, defaulting to str(value) == {ret_val}", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
