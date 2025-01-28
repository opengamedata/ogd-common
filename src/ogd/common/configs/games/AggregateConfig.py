# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.games.FeatureConfig import FeatureConfig
from ogd.common.utils.typing import Map

class AggregateConfig(FeatureConfig):
    def __init__(self, name:str, other_elements:Optional[Map]=None):
        super().__init__(name=name, other_elements=other_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *{self.ReturnType}*, *Aggregate feature* {' (disabled)' if not len(self.Enabled) > 0 else ''}  \n{self.Description}  \n"
        if len(self.Subfeatures) > 0:
            ret_val += "*Sub-features*:  \n\n" + "\n".join([subfeature.AsMarkdown for subfeature in self.Subfeatures.values()])
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "AggregateConfig":
        return AggregateConfig(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "AggregateConfig":
        return AggregateConfig(
            name="DefaultAggregateConfig",
            other_elements={}
        )
