# import standard libraries
import logging
from typing import Any, Dict, Final, Optional, Self, Set
# import local files
from ogd.common.models.features.AggregationMode import AggregationMode
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.schemas.events.DataElementSchema import DataElementSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class FeatureSchema(Schema):
    """
    Dumb struct to contain a specification of an Event in a LoggingSpecificationSchema file.

    These essentially are just a description of the event, and a set of elements in the EventData attribute of the Event.
    """
    _DEFAULT_DESCRIPTION    : Final[str]                  = "Default feature schema. Does not relate to any actual data."
    _DEFAULT_VALUE_TYPE     : Final[str]                  = "UNKNOWN VALUE TYPE"
    _DEFAULT_AGG_LEVELS     : Final[Set[AggregationMode]] = set()
    _DEFAULT_ITER_COUNT     : Final[None]                 = None
    _DEFAULT_ITER_PREFIX    : Final[None]                 = None
    _DEFAULT_MODULE_NAME    : Final[str]                  = "UNKNOWN EXTRACTOR MODULE"
    _DEFAULT_MODULE_VERSION : Final[SemanticVersion]      = SemanticVersion.FromString("UNKNOWN VERSION")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 feature_name:str,              description:Optional[str],
                 value_type:Optional[str],      aggregation_levels:Set[AggregationMode],
                 iteration_count:Optional[int], iteration_prefix:Optional[str],
                 module_name:Optional[str],     module_version:Optional[SemanticVersion],
                 other_elements:Optional[Map]=None):
        """Constructor for the `FeatureSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        TODO: this is just a copy-paste right now.
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
        :param feature_name: _description_
        :type feature_name: str
        :param description: _description_
        :type description: Optional[str]
        :param value_type: _description_
        :type value_type: Optional[str]
        :param aggregation_levels: _description_
        :type aggregation_levels: Set[AggregationMode]
        :param iteration_count: _description_
        :type iteration_count: Optional[int]
        :param iteration_prefix: _description_
        :type iteration_prefix: Optional[str]
        :param module_name: _description_
        :type module_name: Optional[str]
        :param module_version: _description_
        :type module_version: Optional[SemanticVersion]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._feature_name       : str                  = feature_name       if feature_name       is not None else self._parseFeatureName(unparsed_elements=unparsed_elements, schema_name=name)
        self._description        : str                  = description        if description        is not None else self._parseDescription(unparsed_elements=unparsed_elements, schema_name=name)
        self._value_type         : str                  = value_type         if value_type         is not None else self._parseValueType(unparsed_elements=unparsed_elements, schema_name=name)
        self._aggregation_levels : Set[AggregationMode] = aggregation_levels if aggregation_levels is not None else self._parseAggregationLevels(unparsed_elements=unparsed_elements, schema_name=name)
        self._iteration_count    : Optional[int]        = iteration_count    if iteration_count    is not None else self._parseIterationCount(unparsed_elements=unparsed_elements, schema_name=name)
        self._iteration_prefix   : Optional[str]        = iteration_prefix   if iteration_prefix   is not None else self._parseIterationPrefix(unparsed_elements=unparsed_elements, schema_name=name)
        self._module_name        : str                  = module_name        if module_name        is not None else self._parseModuleName(unparsed_elements=unparsed_elements, schema_name=name)
        self._module_version     : SemanticVersion      = module_version     if module_version     is not None else self._parseModuleVersion(unparsed_elements=unparsed_elements, schema_name=name)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def FeatureName(self) -> str:
        return self._feature_name
    @property
    def Description(self) -> str:
        return self._description
    @property
    def ValueType(self) -> str:
        return self._value_type
    @property
    def AggregationLevels(self) -> Set[AggregationMode]:
        return self._aggregation_levels
    @property
    def IterationCount(self) -> Optional[int]:
        return self._iteration_count
    @property
    def IterationPrefix(self) -> Optional[str]:
        return self._iteration_prefix
    @property
    def ModuleName(self) -> str:
        return self._module_name
    @property
    def ModuleVersion(self) -> SemanticVersion:
        return self._module_version

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        return "\n\n".join([
            f"### **{self.FeatureName}**",

            self.Description,

            "#### Feature Data",
            
            "\n".join([
                f"Type: {self.ValueType}",
                f"Exists at {', '.join(str(level) for level in self.AggregationLevels)} levels",
                f"There are {self.IterationCount} instances of this feature, with names formatted as {self.IterationPrefix}##_{self.FeatureName}"
            ]),

            "#### Feature Traceability"

            f"Generated by version {self.ModuleVersion} of the {self.ModuleName} module."
        ])

    @property
    def AsMarkdownRow(self) -> str:
        ret_val = [
            f"### **{self.Name}**",
            f"{self.Description}",
            "#### Event Data",
            "\n".join(
                ["| **Name** | **Value Type** | **Description** | **Iterations** |",
                 "| ---      | ---            | ---             | ---            |"]
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
        return EventSchema(name=name, description=None, event_data=None, other_elements=unparsed_elements)

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
    def _parseEventDataElements(unparsed_elements:Map, schema_name:Optional[str]=None):
        ret_val : Dict[str, DataElementSchema]
        event_data : Dict[str, Any] = EventSchema.ParseElement(
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
    def _parseDescription(unparsed_elements:Map, schema_name:Optional[str]=None):
        return EventSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=EventSchema._DEFAULT_DESCRIPTION,
            remove_target=True,
            schema_name=schema_name
        )

    # *** PRIVATE METHODS ***
