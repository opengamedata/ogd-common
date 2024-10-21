# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.games.FeatureSchema import FeatureSchema
from ogd.common.utils.Logger import Logger

class PerCountSchema(FeatureSchema):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, count:int|str, prefix:str, other_elements:Dict[str, Any]):
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

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "PerCountSchema":
        _count  : int | str
        _prefix : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Per-count Feature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "count" in all_elements.keys():
            _count = PerCountSchema._parseCount(all_elements["count"])
        else:
            _count = 0
            Logger.Log(f"{name} config does not have a 'count' element; defaulting to count={_count}", logging.WARN)
        if "prefix" in all_elements.keys():
            _prefix = PerCountSchema._parsePrefix(all_elements['prefix'])
        else:
            _prefix = "pre"
            Logger.Log(f"{name} config does not have a 'prefix' element; defaulting to prefix='{_prefix}'", logging.WARN)

        _used = {"count", "prefix"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return PerCountSchema(name=name, count=_count, prefix=_prefix, other_elements=_leftovers)

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
