# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.games.FeatureConfig import FeatureConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class PerCountConfig(FeatureSchema):

    _DEFAULT_COUNT = 1
    _DEFAULT_PREFIX = "pre"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, count:int|str, prefix:str, other_elements:Optional[Map]=None):
        self._count  : int | str = count
        self._prefix : str       = prefix

        super().__init__(name=name, other_elements=other_elements)

    @property
    def Count(self) -> int | str:
        return self._count

    @property
    def Prefix(self) -> str:
        return self._prefix

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *{self.ReturnType}*, *Per-count feature* {' (disabled)' if not len(self.Enabled) > 0 else ''}  \n{self.Description}  \n"
        if len(self.Subfeatures) > 0:
            ret_val += "*Sub-features*:  \n\n" + "\n".join([subfeature.AsMarkdown for subfeature in self.Subfeatures.values()])
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "PerCountConfig":
        _count  : int | str
        _prefix : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Per-count Feature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        _count = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["count"],
            parser_function=cls._parseCount,
            default_value=cls._DEFAULT_COUNT
        )
        _prefix = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["prefix"],
            parser_function=cls._parsePrefix,
            default_value=cls._DEFAULT_PREFIX
        )

        _used = {"count", "prefix"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return PerCountConfig(name=name, count=_count, prefix=_prefix, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "PerCountConfig":
        return PerCountConfig(
            name="DefaultPerCountSchema",
            count=cls._DEFAULT_COUNT,
            prefix=cls._DEFAULT_PREFIX,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseCount(count) -> int | str:
        ret_val : int | str
        if isinstance(count, int):
            ret_val = count
        elif isinstance(count, str):
            ret_val = count
        else:
            ret_val = 0
            Logger.Log(f"Extractor count was unexpected type {type(count)}, defaulting to count=0.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePrefix(prefix) -> str:
        ret_val : str
        if isinstance(prefix, str):
            ret_val = prefix
        else:
            ret_val = str(prefix)
            Logger.Log(f"Extractor prefix was unexpected type {type(prefix)}, defaulting to str(prefix).", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
