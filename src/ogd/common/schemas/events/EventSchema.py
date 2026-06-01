# import standard libraries
import logging
from typing import Any, Dict, Final, Optional, Self
# import local files
from ogd.common.schemas.events.DataElementSchema import DataElementSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.models.events.Event import EventSource as EventSourceEnum
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import JSONMap, Map

class EventSchema(Schema):
    """
    Dumb struct to contain a specification of an Event in a LoggingSpecificationSchema file.

    These essentially are just a description of the event, and a set of elements in the EventData attribute of the Event.
    """
    _DEFAULT_DESCRIPTION    : Final[str] = "Default event schema object. Does not relate to any actual data."
    _DEFAULT_EVENT_DATA     : Final[Dict[str, DataElementSchema]] = {}
    _DEFAULT_EVENT_SOURCE   : Final[EventSourceEnum] = EventSourceEnum.GAME
    _DEFAULT_MODULE_NAME    : Final[None] = None
    _DEFAULT_MODULE_VERSION : Final[None] = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,            event_data:Optional[Dict[str, DataElementSchema]],
                 description:Optional[str], event_source:Optional[EventSourceEnum],
                 module_name:Optional[str], module_version:Optional[SemanticVersion],
                 other_elements:Optional[Map]=None):
        """Constructor for the `EventSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "description": "Description of what the event is and when it occurs.",
            "event_data": {
                "data_element_name": {
                "type": "bool",
                "description": "Description of what the data element means or represents."
                }
            }
        },
        ```

        :param name: _description_
        :type name: str
        :param description: _description_
        :type description: Optional[str]
        :param event_data: _description_
        :type event_data: Optional[Dict[str, DataElementSchema]]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._description : str                          = self._getDescription(raw_val=description, unparsed_elements=unparsed_elements, schema_name=name)
        self._event_data  : Dict[str, DataElementSchema] = self._getEventDataElements(raw_val=event_data, unparsed_elements=unparsed_elements, schema_name=name)
        self._source      : EventSourceEnum              = self._getSource(raw_val=event_source, unparsed_elements=unparsed_elements, schema_name=name)
        self._module_name : Optional[str]                = self._getModuleName(raw_val=module_name, unparsed_elements=unparsed_elements, schema_name=name)
        self._mod_version : Optional[SemanticVersion]    = self._getModuleVersion(raw_val=module_version, unparsed_elements=unparsed_elements, schema_name=name)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def EventName(self) -> str:
        """Alias for the EventSchema's name.

        In general, we structure data such that the name of the schema is the same as the event it's describing.
        However, it may also be more readable in some cases to use "EventName" for clarity,
        e.g. when dealing with schemas for events that came from detectors.

        :return: _description_
        :rtype: str
        """
        return self.Name

    @property
    def Description(self) -> str:
        return self._description

    @property
    def EventData(self) -> Dict[str, DataElementSchema]:
        return self._event_data

    @property
    def EventSource(self) -> EventSourceEnum:
        return self._source

    @property
    def ModuleName(self) -> Optional[str]:
        """Property to get the name of the detector module that generates this event.

        :return: The name of the detector module that generates this event, if this is a generated event, or None if it is a game event.
        :rtype: Optional[str]
        """
        return self._module_name

    @property
    def ModuleVersion(self) -> Optional[SemanticVersion]:
        """Property to get the version of the detector module that generates this event.

        :return: The version of the detector module that generates this event, if this is a generated event, or None if it is a game event.
        :rtype: Optional[SemanticVersion]
        """
        return self._mod_version

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        return "\n\n".join([
            f"### **{self.Name}**",
            self.Description,
            "#### Event Data",
            "\n".join(
                  [elem.AsMarkdown for elem in self.EventData.values()]
                + (["- Other Elements:"] +
                   [f"  - **{elem_name}**: {elem_desc}" for elem_name,elem_desc in self.NonStandardElements]
                  ) if len(self.NonStandardElements) > 0 else []
            )
        ])

    @property
    def AsMarkdownTable(self) -> str:
        ret_val = [
            f"### **{self.Name}**",
            f"{self.Description}",
            "#### Event Data",
            "\n".join(
                ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                 "| ---      | ---      | ---             | ---         |"]
              + [elem.AsMarkdownRow for elem in self.EventData.values()]
            ),
        ]
        if len(self.NonStandardElements) > 0:
            ret_val.append("#### Other Elements")
            ret_val.append(
                "\n".join( [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.NonStandardElements] )
            )
        return "\n\n".join(ret_val)

    @property
    def AsDict(self) -> JSONMap:
        ret_val : Dict[str, Any] = {
            "description":self.Description,
            "event_data":{ key:val.AsDict for key,val in self.EventData.items() },
            "event_source":self.EventSource.name,
        }

        if self.ModuleName and self.ModuleVersion:
            ret_val["module_name"] = self.ModuleName
            ret_val["module_version"] = str(self.ModuleVersion)

        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "EventSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: EventSchema
        """
        return EventSchema(name=name,        description=None,
                           event_data=None,  event_source=None,
                           module_name=None, module_version=None,
                           other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "EventSchema":
        return EventSchema(
            name="DefaultEventSchema",
            description=cls._DEFAULT_DESCRIPTION,
            event_data=cls._DEFAULT_EVENT_DATA,
            event_source=cls._DEFAULT_EVENT_SOURCE,
            module_name=cls._DEFAULT_MODULE_NAME,
            module_version=cls._DEFAULT_MODULE_VERSION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _getEventDataElements(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None):
        ret_val : Dict[str, DataElementSchema]
        event_data : Dict[str, Any] = EventSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["event_data"],
            to_type=dict,
            default_value=EventSchema._DEFAULT_EVENT_DATA,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(event_data, dict):
            ret_val = {
                name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
                for name,elems in event_data.items()
            }
        else:
            ret_val = {}
            Logger.Log(f"event_data was unexpected type {type(event_data)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _getDescription(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> str:
        return EventSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=EventSchema._DEFAULT_DESCRIPTION,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _getSource(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None):
        ret_val : EventSourceEnum

        raw_source = EventSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["event_source", "source"],
            to_type=str,
            default_value=EventSchema._DEFAULT_EVENT_SOURCE,
            remove_target=True,
            schema_name=schema_name
        )

        if isinstance(raw_source, str):
            ret_val = EventSourceEnum[raw_source]
        else:
            Logger.Log(f"In EventSchema, raw event source was unexpected type {type(raw_source)}, using EventSource[str(raw_source)]")
            ret_val = EventSourceEnum[str(raw_source)]

        return ret_val

    @staticmethod
    def _getModuleName(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None):
        return EventSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["module_name", "detector_name"],
            to_type=str,
            default_value=EventSchema._DEFAULT_MODULE_NAME,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )

    @staticmethod
    def _getModuleVersion(raw_val:Any, unparsed_elements:Map, schema_name:Optional[str]=None) -> Optional[SemanticVersion]:
        ret_val : Optional[SemanticVersion]

        raw_ver = EventSchema.ParseElement(
            raw_value=raw_val,
            unparsed_elements=unparsed_elements,
            valid_keys=["module_version", "detector_version"],
            to_type=str,
            default_value=EventSchema._DEFAULT_MODULE_VERSION,
            remove_target=True,
            schema_name=schema_name,
            optional_element=True
        )
        if raw_ver == None:
            ret_val = None
        elif isinstance(raw_ver, str):
            ret_val = SemanticVersion.FromString(raw_ver)
        else:
            Logger.Log(f"In EventSchema, raw module version was unexpected type {type(raw_ver)}, using SemanticVersion.FromString(str(raw_ver))")
            ret_val = SemanticVersion.FromString(str(raw_ver))

        return ret_val

    # *** PRIVATE METHODS ***
