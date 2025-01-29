# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.games.GeneratorConfig import GeneratorConfig
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class SubfeatureConfig(Schema):
    _DEFAULT_RETURN_TYPE = "str"
    _DEFAULT_DESCRIPTION = "Default Subfeature schema object. Does not correspond to any actual data."

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, return_type:str, description:str, other_elements:Optional[Map]=None):
        self._return_type : str = return_type or self._parseReturnType(unparsed_elements=other_elements or {})
        self._description : str = description or self._parseDescription(unparsed_elements=other_elements or {})

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
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "SubfeatureConfig":
        _return_type : str
        _description : str    

        if not isinstance(unparsed_elements, dict):
            _elements = {}
            Logger.Log(f"For {name} subfeature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        _return_type = cls._parseReturnType(unparsed_elements=unparsed_elements)
        _description = cls._parseDescription(unparsed_elements=unparsed_elements)

        _used = {"return_type", "description"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return SubfeatureConfig(name=name, return_type=_return_type, description=_description, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "SubfeatureConfig":
        return SubfeatureConfig(
            name="DefaultSubFeatureConfig",
            return_type=cls._DEFAULT_RETURN_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseReturnType(unparsed_elements:Map) -> str:
        return SubfeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["return_type"],
            to_type=str,
            default_value=SubfeatureConfig._DEFAULT_RETURN_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseDescription(unparsed_elements:Map):
        return SubfeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=SubfeatureConfig._DEFAULT_DESCRIPTION,
            remove_target=True
        )

    # *** PRIVATE METHODS ***

class FeatureConfig(GeneratorConfig):
    """Base class for all schemas related to defining feature Extractor configurations.
    """
    _DEFAULT_RETURN_TYPE = "str"
    _DEFAULT_SUBFEATURES = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, return_type:str, subfeatures:Dict[str, SubfeatureConfig], other_elements:Optional[Map]=None):
        self._subfeatures : Dict[str, SubfeatureConfig]
        self._return_type : str

        if not isinstance(other_elements, dict):
            other_elements = {}
            Logger.Log(f"For {name} Feature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        self._return_type = return_type or FeatureConfig._parseReturnType(unparsed_elements=other_elements)
        self._subfeatures = subfeatures or FeatureConfig._parseSubfeatures(unparsed_elements=other_elements)

        _used = {"return_type", "subfeatures"}
        _leftovers = { key : val for key,val in other_elements.items() if key not in _used }

        super().__init__(name=name, other_elements=_leftovers)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Subfeatures(self) -> Dict[str, SubfeatureConfig]:
        return self._subfeatures

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseReturnType(unparsed_elements:Map) -> str:
        return FeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["return_type"],
            to_type=str,
            default_value=FeatureConfig._DEFAULT_RETURN_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseSubfeatures(unparsed_elements) -> Dict[str, SubfeatureConfig]:
        ret_val : Dict[str, SubfeatureConfig]

        subfeatures = FeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["subfeatures"],
            to_type=dict,
            default_value=FeatureConfig._DEFAULT_SUBFEATURES,
            remove_target=True
        )
        if isinstance(subfeatures, dict):
            ret_val = {name:SubfeatureConfig.FromDict(name=name, unparsed_elements=elems) for name,elems in subfeatures.items()}
        else:
            ret_val = {}
            Logger.Log(f"Extractor subfeatures was unexpected type {type(subfeatures)}, defaulting to empty list.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
