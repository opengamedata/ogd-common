# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class ColumnSchema(Schema):
    _DEFAULT_READABLE = "Default Column Schema Name"
    _DEFAULT_VALUE_TYPE = "TYPE NOT GIVEN"
    _DEFAULT_DESCRIPTION = "NO DESCRIPTION GIVEN"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, readable:str, value_type:str, description:str, other_elements:Optional[Map]=None):
        self._readable    : str = readable
        self._value_type  : str = value_type
        self._description : str = description

        super().__init__(name=name, other_elements=other_elements)

    def __str__(self):
        return self.Name

    def __repr__(self):
        return self.Name

    @property
    def ReadableName(self) -> str:
        return self._name

    @property
    def Description(self) -> str:
        return self._description

    @property
    def ValueType(self) -> str:
        return self._value_type

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val = f"**{self.Name}** : *{self.ValueType}* - {self.ReadableName}, {self.Description}  "

        if len(self.NonStandardElements) > 0:
            other_elems = [f"{key}: {val}" for key,val in self.NonStandardElements]
            ret_val += f"\n    Other Elements: {', '.join(other_elems)}"

        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "ColumnSchema":
        _readable    : str
        _value_type  : str
        _description : str

        if not isinstance(all_elements, dict):
            # _name        = "No Name"
            # _readable    = "No Readable Name"
            # _description = "No Description"
            # _value_type  = "No Type"
            all_elements = {}
            _msg = f"For {name} Extractor config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)

        _readable = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["readable"],
            to_type=cls._parseReadable,
            default_value=name
        )
        _description = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["description"],
            to_type=cls._parseDescription,
            default_value="NO DESCRIPTION GIVEN"
        )
        _value_type = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["type"],
            to_type=cls._parseValueType,
            default_value="TYPE NOT GIVEN"
        )
        _name = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["name"],
            to_type=cls._parseString,
            default_value=name
        )
        _used = {"name", "readable", "description", "type"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }

        return ColumnSchema(name=_name, readable=_readable, value_type=_value_type, description=_description, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "ColumnSchema":
        return ColumnSchema(
            name="DefaultColumnSchema",
            readable=cls._DEFAULT_READABLE,
            value_type=cls._DEFAULT_VALUE_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseString(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Column name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseReadable(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Column readable name was not a string, defaulting to str(readable) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Column description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseValueType(extractor_type):
        ret_val : str
        if isinstance(extractor_type, str):
            ret_val = extractor_type
        else:
            ret_val = str(extractor_type)
            Logger.Log(f"Column type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
