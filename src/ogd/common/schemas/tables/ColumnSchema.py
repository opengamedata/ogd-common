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
        unparsed_elements : Map = other_elements or {}

        self._readable    : str = readable    or self._parseReadable(unparsed_elements=unparsed_elements)
        self._value_type  : str = value_type  or self._parseValueType(unparsed_elements=unparsed_elements)
        self._description : str = description or self._parseDescription(unparsed_elements=unparsed_elements)

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
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "ColumnSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: ColumnSchema
        """
        _readable    : str = cls._parseReadable(unparsed_elements=unparsed_elements)
        _description : str = cls._parseDescription(unparsed_elements=unparsed_elements)
        _value_type  : str = cls._parseValueType(unparsed_elements=unparsed_elements)
        _name        : str = cls._parseName(name=name, unparsed_elements=unparsed_elements)

        _used = {"name", "readable", "description", "type"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }

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
    def _parseName(name:str, unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["name"],
            to_type=str,
            default_value=name,
            remove_target=True
        )
    
    @staticmethod
    def _parseReadable(unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["readable", "human_readable"],
            to_type=str,
            default_value=ColumnSchema._DEFAULT_READABLE,
            remove_target=True
        )
    
    @staticmethod
    def _parseDescription(unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=ColumnSchema._DEFAULT_DESCRIPTION,
            remove_target=True
        )
    
    @staticmethod
    def _parseValueType(unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["type"],
            to_type=str,
            default_value=ColumnSchema._DEFAULT_VALUE_TYPE,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
