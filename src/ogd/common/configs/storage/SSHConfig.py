# import standard libraries
from typing import Dict, Optional
from urllib.parse import ParseResult
# import local files
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.utils.typing import Map

class SSHConfig(DataStoreConfig):
    _STORE_TYPE = "SSH"
    _DEFAULT_LOCATION = URLLocationSchema(
        name="DefaultSSHLocation",
        url=ParseResult(
            scheme="http",
            netloc="127.0.0.1:22",
            path="", params="", query="", fragment=""
        )
    )
    _DEFAULT_CREDENTIAL = PasswordCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 location:URLLocationSchema, ssh_credential:PasswordCredential,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._location   : URLLocationSchema  = location       or self._parseLocation(unparsed_elements=unparsed_elements)
        self._credential : PasswordCredential = ssh_credential or self._parseCredential(unparsed_elements=unparsed_elements)
        super().__init__(name=name, store_type=self._STORE_TYPE, other_elements=other_elements)

    @property
    def Host(self) -> Optional[str]:
        return self._location.Host

    @property
    def User(self) -> str:
        return self._credential.User

    @property
    def Pass(self) -> Optional[str]:
        return self._credential.Pass

    @property
    def Port(self) -> Optional[int]:
        return self._location.Port

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> URLLocationSchema:
        return self._location

    @property
    def Credential(self) -> PasswordCredential:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name} : `{self.AsConnectionInfo}`"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str

        ret_val = f"{self.User}@{self.Host}:{self.Port}"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "SSHConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: SSHConfig
        """
        _location   : URLLocationSchema  = cls._parseLocation(unparsed_elements=unparsed_elements)
        _credential : PasswordCredential = cls._parseCredential(unparsed_elements=unparsed_elements)

        return SSHConfig(name=name, location=_location, ssh_credential=_credential, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "SSHConfig":
        return SSHConfig(
            name="DefaultSSHConfig",
            location=SSHConfig._DEFAULT_LOCATION,
            ssh_credential=SSHConfig._DEFAULT_CREDENTIAL,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseLocation(unparsed_elements:Map) -> URLLocationSchema:
        _overrides = {"host":"SSH_HOST", "port":"SSH_PORT"}

        return URLLocationSchema.FromDict(
            name              =  "SSHHostLocation",
            unparsed_elements = unparsed_elements,
            key_overrides     = _overrides
        )

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> PasswordCredential:
        _overrides = { "USER":"SSH_USER", "PASS":"SSH_PASS", "PW":"SSH_PW" }

        return PasswordCredential.FromDict(
            name="SSHCredential",
            unparsed_elements=unparsed_elements,
            key_overrides=_overrides
        )

    # *** PRIVATE METHODS ***
