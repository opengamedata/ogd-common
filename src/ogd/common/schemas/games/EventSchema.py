# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.games.DataElementSchema import DataElementSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class EventSchema(Schema):

    # *** BUILT-INS & PROPERTIES ***

    """
    Dumb struct to contain a specification of an Event in a GameSchema file.

    These essentially are just a description of the event, and a set of elements in the EventData attribute of the Event.
    """
    def __init__(self, name:str, description:str, event_data:Dict[str, DataElementSchema], other_elements:Dict[str, Dict]):
        self._description : str                          = description
        self._event_data  : Dict[str, DataElementSchema] = event_data

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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "EventSchema":
        _description : str
        _event_data  : Dict[str, DataElementSchema]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Event config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        _description = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["description"],
            parser_function=cls._parseDescription,
            default_value="No description available"
        )
        _event_data = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["event_data"],
            parser_function=cls._parseEventDataElements,
            default_value={}
        )

        _used = {"description", "event_data"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return EventSchema(name=name, description=_description, event_data=_event_data, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseEventDataElements(event_data):
        ret_val : Dict[str, DataElementSchema]
        if isinstance(event_data, dict):
            ret_val = {name:DataElementSchema.FromDict(name=name, all_elements=elems) for name,elems in event_data.items()}
        else:
            ret_val = {}
            Logger.Log(f"event_data was unexpected type {type(event_data)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Event description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
