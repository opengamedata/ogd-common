# import standard libraries
from typing import Dict, Optional
# import local files
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.utils.typing import Map


class PasswordCredential(CredentialConfig):
    """Dumb struct to contain data pertaining to credentials for accessing a data source.

    In general, a credential can have a key, or a user-password combination.
    """
    _DEFAULT_USER = "DEFAULT USER"
    _DEFAULT_PASS = None

    def __init__(self, name:str, username:str, password:Optional[str], other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}
        self._user = username or self._parseUser(unparsed_elements=unparsed_elements)
        self._pass = password or self._parsePass(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=unparsed_elements)

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

        ret_val = f"User : `{self.User}`\nPass: `*** HIDDEN ***`"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "PasswordCredential":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: PasswordCredential
        """
        _user : str           = cls._parseUser(unparsed_elements=unparsed_elements)
        _pass : Optional[str] = cls._parsePass(unparsed_elements=unparsed_elements)

        return PasswordCredential(name=name, username=_user, password=_pass, other_elements=unparsed_elements)

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
    def _parseUser(unparsed_elements:Map) -> str:
        return PasswordCredential.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["USER"],
            to_type=str,
            default_value=PasswordCredential._DEFAULT_USER,
            remove_target=True
        )

    @staticmethod
    def _parsePass(unparsed_elements:Map) -> str:
        return PasswordCredential.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PASS", "PASSWORD", "PW"],
            to_type=str,
            default_value=PasswordCredential._DEFAULT_PASS,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
