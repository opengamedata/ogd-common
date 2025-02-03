# import standard libraries
import logging
from typing import Any, Dict
# import local files
from ogd.common.configs.Config import Config
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class EmptyCredential(Config):
    """Dumb struct to contain data pertaining to credentials for accessing a data source.

    In general, a credential can have a key, or a user-password combination.
    """
    # @overload
    # def __init__(self, name:str, other_elements:Dict[str, Any]): ...

    def __init__(self, name:str, other_elements:Dict[str, Any] | Any):
        super().__init__(name=name, other_elements=other_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self._name} Empty Credential"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Map)-> "EmptyCredential":
        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} empty credential config, all_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        return EmptyCredential(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "EmptyCredential":
        return EmptyCredential(
            name="DefaultEmptyCredential",
            other_elements={}
        )
