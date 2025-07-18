# import standard libraries
from typing import Dict, Optional
# import local files
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.utils.typing import Map

class SSHConfig(Schema):
    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 22
    _DEFAULT_LOCATION = URLLocationSchema(
        name="DefaultSSHLocation",
        host_name=_DEFAULT_HOST,
        port=_DEFAULT_PORT,
        path=""
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
        super().__init__(name=name, other_elements=other_elements)

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
    def Port(self) -> int:
        return self._location.Port

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

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
        ret_val : URLLocationSchema

        raw_host = SSHConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SSH_HOST"],
            to_type=str,
            default_value=SSHConfig._DEFAULT_HOST,
            remove_target=True
        )
        raw_port = SSHConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SSH_PORT"],
            to_type=int,
            default_value=SSHConfig._DEFAULT_PORT,
            remove_target=True
        )
        if raw_host and raw_port:
            ret_val = URLLocationSchema(
                name      = "SSHHostLocation",
                host_name = raw_host or URLLocationSchema._DEFAULT_HOST_NAME,
                port      = raw_port or URLLocationSchema._DEFAULT_PORT,
                path      = ""
            )
        else:
            ret_val = URLLocationSchema.FromDict(name="SSHHostLocation", unparsed_elements=unparsed_elements)
        
        return ret_val

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> PasswordCredential:
        ret_val : PasswordCredential

        _cred_elements = SSHConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SSH_CREDENTIAL"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if _cred_elements:
            ret_val = PasswordCredential.FromDict(name="SSHCredential", unparsed_elements=_cred_elements)
        else:
            ret_val = SSHConfig._DEFAULT_CREDENTIAL

        return ret_val

    # *** PRIVATE METHODS ***
