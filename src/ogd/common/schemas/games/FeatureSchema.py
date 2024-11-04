# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.games.GeneratorSchema import GeneratorSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class SubfeatureSchema(Schema):
    _DEFAULT_RETURN_TYPE = "str",
    _DEFAULT_DESCRIPTION = "Default Subfeature schema object. Does not correspond to any actual data."

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, return_type:str, description:str, other_elements:Dict[str, str]):
        self._return_type : str = return_type
        self._description : str = description

        super().__init__(name=name, other_elements=other_elements)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Description(self) -> str:
        return self._description

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ReturnType}*, {self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += f'   (other items: {self.NonStandardElements}'
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "FileIndexingSchema":
        _return_type : str
        _description : str    

        if not isinstance(all_elements, dict):
            _elements = {}
            Logger.Log(f"For {name} subfeature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        _return_type = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["return_type"],
            parser_function=cls._parseReturnType,
            default_value=cls._DEFAULT_RETURN_TYPE
        )
        _description = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["description"],
            parser_function=cls._parseDescription,
            default_value=cls._DEFAULT_DESCRIPTION
        )

        _used = {"return_type", "description"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return SubfeatureSchema(name=name, return_type=_return_type, description=_description, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "SubfeatureSchema":
        return SubfeatureSchema(
            name="DefaultSubfeatureSchema",
            return_type=cls._DEFAULT_RETURN_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

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

    # *** PRIVATE METHODS ***

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
