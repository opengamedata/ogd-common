# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class DataElementSchema(Schema):
    """
    Dumb struct to contain a specification of a data element from the EventData, GameState, or UserData attributes of an Event.
    """

    _DEFAULT_TYPE = "str"
    _DEFAULT_DESCRIPTION = "Default data element generated the DataElementSchema class. Does not represent actual data."
    _DEFAULT_DETAILS = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, element_type:str, description:str, details:Optional[Dict[str, str]], other_elements:Optional[Map]=None):
        self._type        : str                      = element_type
        self._description : str                      = description
        self._details     : Optional[Dict[str, str]] = details

        super().__init__(name=name, other_elements=other_elements)

    @property
    def ElementType(self) -> str:
        return self._type

    @property
    def Description(self) -> str:
        return self._description

    @property
    def Details(self) -> Optional[Dict[str, str]]:
        return self._details

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ElementType}*, {self.Description}"
        if self.Details is not None:
            detail_markdowns = [f"    - **{name}** - {desc}  " for name,desc in self.Details.items()]
            detail_joined = '\n'.join(detail_markdowns)
            ret_val += f"  \n  Details:  \n{detail_joined}"
        return ret_val

    @property
    def AsMarkdownRow(self) -> str:
        ret_val : str = f"| {self.Name} | {self.ElementType} | {self.Description} |"
        if self.Details is not None:
            detail_markdowns = [f"**{name}** : {desc}" for name,desc in self.Details.items()]
            ret_val += ', '.join(detail_markdowns)
        ret_val += " |"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "DataElementSchema":
        _type        : str
        _description : str
        _details     : Optional[Dict[str, str]]

        if not isinstance(all_elements, dict):
            if isinstance(all_elements, str):
                all_elements = { 'description' : all_elements }
                Logger.Log(f"For EventDataElement config of `{name}`, all_elements was a str, probably in legacy format. Defaulting to all_elements = {'{'} description : {all_elements['description']} {'}'}", logging.WARN)
            else:
                all_elements = {}
                Logger.Log(f"For EventDataElement config of `{name}`, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        _type = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["type"],
            parser_function=cls._parseElementType,
            default_value=cls._DEFAULT_TYPE
        )
        _description = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["description"],
            parser_function=cls._parseDescription,
            default_value=cls._DEFAULT_DESCRIPTION
        )
        _details = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["details"],
            parser_function=cls._parseDetails,
            default_value=cls._DEFAULT_DETAILS
        )

        _used = {"type", "description", "details"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return DataElementSchema(name=name, element_type=_type, description=_description, details=_details, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "DataElementSchema":
        return DataElementSchema(
            name="DefaultDataElementSchema",
            element_type=cls._DEFAULT_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            details=cls._DEFAULT_DETAILS,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseElementType(event_type):
        ret_val : str
        if isinstance(event_type, str):
            ret_val = event_type
        else:
            ret_val = str(event_type)
            Logger.Log(f"EventDataElement type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"EventDataElement description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDetails(details):
        ret_val : Dict[str, str] = {}
        if isinstance(details, dict):
            for key,val in details.items():
                if isinstance(key, str):
                    if isinstance(val, str):
                        ret_val[key] = val
                    else:
                        ret_val[key] = str(val)
                        Logger.Log(f"EventDataElement detail value for key {key} was unexpected type {type(val)}, defaulting to str(val) == {ret_val[key]}", logging.WARN)
                else:
                    _key = str(key)
                    Logger.Log(f"EventDataElement detail key was unexpected type {type(key)}, defaulting to str(key) == {_key}", logging.WARN)
                    if isinstance(val, str):
                        ret_val[_key] = val
                    else:
                        ret_val[_key] = str(val)
                        Logger.Log(f"EventDataElement detail value for key {_key} was unexpected type {type(val)}, defaulting to str(val) == {ret_val[_key]}", logging.WARN)
        else:
            ret_val = {}
            Logger.Log("EventDataElement details was not a dict, defaulting to empty dict.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***

