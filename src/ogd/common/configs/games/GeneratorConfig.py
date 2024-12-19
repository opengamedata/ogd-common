# import standard libraries
import logging
from typing import Optional, Set
# import local files
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class GeneratorConfig(Schema):
    def __init__(self, name:str, other_elements:Optional[Map]=None):
        self._enabled     : Set[ExtractionMode]
        self._type_name   : str
        self._description : str
        _other_elements = other_elements or {}

        if not isinstance(_other_elements, dict):
            other_elements = {}
            Logger.Log(f"For {name} Extractor config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        if "type" in _other_elements.keys():
            self._type_name = GeneratorConfig._parseType(_other_elements['type'])
        else:
            self._type_name = name
        if "enabled" in _other_elements.keys():
            self._enabled = GeneratorConfig._parseEnabled(_other_elements['enabled'])
        else:
            self._enabled = {ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
            Logger.Log(f"{name} config does not have an 'enabled' element; defaulting to enabled=True", logging.WARN)
        if "description" in _other_elements.keys():
            self._description = GeneratorConfig._parseDescription(_other_elements['description'])
        else:
            self._description = "No Description"
            Logger.Log(f"{name} config does not have an 'description' element; defaulting to description='{self._description}'", logging.WARN)

        _leftovers = { key : val for key,val in _other_elements.items() if key not in {"type", "enabled", "description"} }
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
