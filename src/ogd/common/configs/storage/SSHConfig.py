# import standard libraries
import logging
from pathlib import Path
from typing import Optional
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class SSHConfig(Schema):
    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 22
    _DEFAULT_CREDENTIAL = PasswordCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 ssh_host:Optional[str], ssh_port:int, ssh_credential:PasswordCredential,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._host       : Optional[str]      = ssh_host       or self._parseHost(unparsed_elements=unparsed_elements)
        self._port       : int                = ssh_port       or self._parsePort(unparsed_elements=unparsed_elements)
        self._credential : PasswordCredential = ssh_credential or self._parseCredential(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Host(self) -> Optional[str]:
        return self._host

    @property
    def User(self) -> str:
        return self._credential.User

    @property
    def Pass(self) -> Optional[str]:
        return self._credential.Pass

    @property
    def Port(self) -> int:
        return self._port

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
    def _fromDict(cls, name:str, unparsed_elements:Map)-> "SSHConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: SSHConfig
        """
        _host       : str                = cls._parseHost(unparsed_elements=unparsed_elements)
        _port       : int                = cls._parsePort(unparsed_elements=unparsed_elements)
        _credential : PasswordCredential = cls._parseCredential(unparsed_elements=unparsed_elements)

        return SSHConfig(name=name, ssh_host=_host, ssh_credential=_credential, ssh_port=_port, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "SSHConfig":
        return SSHConfig(
            name="DefaultSSHConfig",
            ssh_host=cls._DEFAULT_HOST,
            ssh_credential=SSHConfig._DEFAULT_CREDENTIAL,
            ssh_port=cls._DEFAULT_PORT,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseHost(unparsed_elements:Map) -> str:
        return SSHConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SSH_HOST"],
            to_type=str,
            default_value=SSHConfig._DEFAULT_HOST,
            remove_target=True
        )

    @staticmethod
    def _parsePort(unparsed_elements:Map) -> int:
        return SSHConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SSH_PORT"],
            to_type=int,
            default_value=SSHConfig._DEFAULT_HOST,
            remove_target=True
        )

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
