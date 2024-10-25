# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.games.GeneratorSchema import GeneratorSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class SubfeatureSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, str]):
        self._return_type : str
        self._description : str    

        if not isinstance(all_elements, dict):
            self._elements = {}
            Logger.Log(f"For {name} subfeature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        if "return_type" in all_elements.keys():
            self._return_type = SubfeatureSchema._parseReturnType(all_elements['return_type'])
        else:
            self._return_type = "Unknown"
            Logger.Log(f"{name} subfeature config does not have an 'return_type' element; defaulting to return_type='{self._return_type}", logging.WARN)
        if "description" in all_elements.keys():
            self._description = SubfeatureSchema._parseDescription(all_elements['description'])
        else:
            self._description = "No description"
            Logger.Log(f"{name} subfeature config does not have an 'description' element; defaulting to description='{self._description}'", logging.WARN)
        
        _used = {"return_type", "description"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Description(self) -> str:
        return self._description

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ReturnType}*, {self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += f'   (other items: {self.NonStandardElements}'
        return ret_val

    @staticmethod
    def _parseReturnType(return_type):
        ret_val : str
        if isinstance(return_type, str):
            ret_val = return_type
        else:
            ret_val = str(return_type)
            Logger.Log(f"Subfeature return_type was not a string, defaulting to str(return_type) == {ret_val}", logging.WARN)
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

class FeatureSchema(GeneratorSchema):
    """Base class for all schemas related to defining feature Extractor configurations.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, other_elements:Dict[str, Any]):
        self._subfeatures : Dict[str, SubfeatureSchema]
        self._return_type : str

        if not isinstance(other_elements, dict):
            other_elements = {}
            Logger.Log(f"For {name} Feature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        self._return_type = FeatureSchema.ElementFromDict(all_elements=other_elements,
            element_names=["return_type"],
            parser_function=FeatureSchema._parseReturnType,
            default_value="UNKNOWN"
        )
        self._subfeatures = FeatureSchema.ElementFromDict(all_elements=other_elements,
            element_names=["subfeatures"],
            parser_function=FeatureSchema._parseSubfeatures,
            default_value={}
        )

        _used = {"return_type", "subfeatures"}
        _leftovers = { key : val for key,val in other_elements.items() if key not in _used }

        super().__init__(name=name, all_elements=_leftovers)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Subfeatures(self) -> Dict[str, SubfeatureSchema]:
        return self._subfeatures

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseReturnType(return_type, feature_name:str=""):
        ret_val : str
        if isinstance(return_type, str):
            ret_val = return_type
        else:
            ret_val = str(return_type)
            Logger.Log(f"Feature {feature_name} return_type was not a string, defaulting to str(return_type) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSubfeatures(subfeatures) -> Dict[str, SubfeatureSchema]:
        ret_val : Dict[str, SubfeatureSchema]
        if isinstance(subfeatures, dict):
            ret_val = {name:SubfeatureSchema.FromDict(name=name, all_elements=elems) for name,elems in subfeatures.items()}
        else:
            ret_val = {}
            Logger.Log(f"Extractor subfeatures was unexpected type {type(subfeatures)}, defaulting to empty list.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
