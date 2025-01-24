# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.Config import Config
from ogd.common.utils.Logger import Logger


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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "EmptyCredential":
        _user : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} empty credential config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        return EmptyCredential(name=name, other_elements=all_elements)

    @classmethod
    def Default(cls) -> "EmptyCredential":
        return EmptyCredential(
            name="DefaultEmptyCredential",
            other_elements={}
        )
