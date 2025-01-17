# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.games.GeneratorConfig import GeneratorConfig
from ogd.common.utils.typing import Map

class DetectorConfig(GeneratorConfig):
    def __init__(self, name:str, other_elements:Optional[Map]=None):
        super().__init__(name=name, other_elements=other_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *Detector* {' (disabled)' if not ExtractionMode.DETECTOR in self.Enabled else ''}  \n{self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "DetectorConfig":
        return DetectorConfig(name=name, other_elements=all_elements)

    @classmethod
    def Default(cls) -> "DetectorConfig":
        return DetectorConfig(name="DefaultDetectorConfig", other_elements={})
