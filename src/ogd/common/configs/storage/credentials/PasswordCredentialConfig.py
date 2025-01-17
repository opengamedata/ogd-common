# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.utils.Logger import Logger


class PasswordCredential(CredentialConfig):
    """Dumb struct to contain data pertaining to credentials for accessing a data source.

    In general, a credential can have a key, or a user-password combination.
    """
    _DEFAULT_USER = "DEFAULT USER"
    _DEFAULT_PASS = None

    def __init__(self, name:str, username:str, password:Optional[str], other_elements:Dict[str, Any] | Any):
        super().__init__(name=name, other_elements=other_elements)
        self._user = username
        self._pass = password

    @property
    def User(self) -> str:
        return self._user

    @property
    def Pass(self) -> Optional[str]:
        return self._pass

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"User : `{self.User}`\nPass: `****`"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "PasswordCredential":
        _user : str
        _pass : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} password credential config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _user = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["USER"],
            parser_function=cls._parseUser,
            default_value=cls._DEFAULT_USER
        )
        _pass = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["PASS"],
            parser_function=cls._parsePass,
            default_value=cls._DEFAULT_PASS
        )

        _used = {"USER", "PASS"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return PasswordCredential(name=name, username=_user, password=_pass, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "PasswordCredential":
        return PasswordCredential(
            name="DefaultPasswordCredential",
            username=cls._DEFAULT_USER,
            password=cls._DEFAULT_PASS,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseUser(user) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(user, str):
            ret_val = user
        else:
            ret_val = str(user)
            Logger.Log(f"User for password credential was unexpected type {type(user)}, defaulting to str(user)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePass(pw) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(pw, str):
            ret_val = pw
        else:
            ret_val = str(pw)
            Logger.Log(f"Password for password credential was unexpected type {type(pw)}, defaulting to str(pw)=***.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
