# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Set
# import local files
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class ExtractorSchema(Schema):
    """Base class for all schemas related to defining Generator configurations.

    TODO : Rename to GeneratorSchema
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._enabled     : Set[ExtractionMode]
        self._type_name   : str
        self._description : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Extractor config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        self._type_name = ExtractorSchema.ElementFromDict(all_elements=all_elements,
            element_names=["type"],
            parser_function=ExtractorSchema._parseType,
            default_value="UNKNOWN"
        )
        self._enabled = ExtractorSchema.ElementFromDict(all_elements=all_elements,
            element_names=["enabled"],
            parser_function=ExtractorSchema._parseEnabled,
            default_value={ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
        )
        self._description = ExtractorSchema.ElementFromDict(all_elements=all_elements,
            element_names=["description"],
            parser_function=ExtractorSchema._parseDescription,
            default_value="No Description"
        )

        _used = {"type", "enabled", "description"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }

        super().__init__(name=name, other_elements=_leftovers)

    @property
    def TypeName(self) -> str:
        return self._type_name

    @property
    def Enabled(self) -> Set[ExtractionMode]:
        return self._enabled

    @property
    def Description(self) -> str:
        return self._description

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseType(extractor_type):
        ret_val : str
        if isinstance(extractor_type, str):
            ret_val = extractor_type
        else:
            ret_val = str(extractor_type)
            Logger.Log(f"Extractor type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseEnabled(enabled):
        ret_val : Set[ExtractionMode] = set()
        if isinstance(enabled, bool):
            if enabled:
                ret_val = {ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
            else:
                ret_val = set()
        elif isinstance(enabled, list):
            for mode in enabled:
                mode = str(mode).upper()
                match mode:
                    case "DETECTOR":
                        ret_val.add(ExtractionMode.DETECTOR)
                    case "SESSION":
                        ret_val.add(ExtractionMode.SESSION)
                    case "PLAYER":
                        ret_val.add(ExtractionMode.PLAYER)
                    case "POPULATION":
                        ret_val.add(ExtractionMode.POPULATION)
                    case _:
                        Logger.Log(f"Found unrecognized element of 'enabled': {mode}", logging.WARN)
        else:
            ret_val = {ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
            Logger.Log(f"'enabled' element has unrecognized type {type(enabled)}; defaulting to enable all modes", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Extractor description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
