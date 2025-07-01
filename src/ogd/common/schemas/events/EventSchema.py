# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.games.DataElementSchema import DataElementSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class EventSchema(Schema):
    _DEFAULT_DESCRIPTION = "Default event schema object. Does not relate to any actual data."
    _DEFAULT_EVENT_DATA = {}

    # *** BUILT-INS & PROPERTIES ***

    """
    Dumb struct to contain a specification of an Event in a GameEventsSchema file.

    These essentially are just a description of the event, and a set of elements in the EventData attribute of the Event.
    """
    def __init__(self, name:str, description:str, event_data:Dict[str, DataElementSchema], other_elements:Optional[Map]=None):
        unparsed_elements = other_elements or {}

        self._description : str                          = description or self._parseDescription(unparsed_elements=unparsed_elements)
        self._event_data  : Dict[str, DataElementSchema] = event_data  or self._parseEventDataElements(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def Description(self) -> str:
        return self._description

    @property
    def EventData(self) -> Dict[str, DataElementSchema]:
        return self._event_data

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

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "EventSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: EventSchema
        """
        _description : str
        _event_data  : Dict[str, DataElementSchema]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            Logger.Log(f"For {name} Event config, unparsed_elements was not a dict, defaulting to empty dict", logging.WARN)
        _description = cls._parseDescription(unparsed_elements=unparsed_elements)
        _event_data = cls._parseEventDataElements(unparsed_elements=unparsed_elements)

        _used = {"description", "event_data"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return EventSchema(name=name, description=_description, event_data=_event_data, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "EventSchema":
        return EventSchema(
            name="DefaultEventSchema",
            description=cls._DEFAULT_DESCRIPTION,
            event_data=cls._DEFAULT_EVENT_DATA,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseEventDataElements(unparsed_elements:Map):
        ret_val : Dict[str, DataElementSchema]
        event_data = EventSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_data"],
            to_type=dict,
            default_value=EventSchema._DEFAULT_EVENT_DATA,
            remove_target=True
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
    def _parseDescription(unparsed_elements:Map):
        return EventSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=EventSchema._DEFAULT_DESCRIPTION,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
