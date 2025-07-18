# import standard libraries
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import ParseResult
# import local files
from ogd.common.configs.storage.SSHConfig import SSHConfig
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.utils.typing import Map

class MySQLConfig(DataStoreConfig):
    _STORE_TYPE = "MYSQL"

    _DEFAULT_LOCATION = URLLocationSchema(
        name="DefaultMySQLLocation",
        url=ParseResult(
            scheme="",
            netloc="127.0.0.1:3306",
            path="", params="", query="", fragment=""
        )
    )
    _DEFAULT_DB_CREDENTIAL = PasswordCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 db_location:URLLocationSchema, db_credential:PasswordCredential, ssh_cfg:"SSHConfig",
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._db_location : URLLocationSchema  = db_location   or self._parseLocation(unparsed_elements=unparsed_elements)
        self._credential  : PasswordCredential = db_credential or self._parseCredential(unparsed_elements=unparsed_elements)
        self._ssh_cfg     : SSHConfig          = ssh_cfg       or self._parseSSHConfig(unparsed_elements=unparsed_elements)
        super().__init__(name=name, store_type=self._STORE_TYPE, other_elements=other_elements)

    @property
    def DBHost(self) -> str:
        return self._db_location.Host

    @property
    def DBPort(self) -> Optional[int]:
        return self._db_location.Port

    @property
    def DBUser(self) -> str:
        return self._credential.User

    @property
    def DBPass(self) -> Optional[str]:
        return self._credential.Pass

    @property
    def SSHConf(self) -> SSHConfig:
        return self._ssh_cfg

    @property
    def SSH(self) -> "SSHConfig":
        """Shortened alias for SSHConfig, convenient when using sub-elements of the SSHConfig.

        :return: The schema describing the configuration for an SSH connection to a data source.
        :rtype: SSHSchema
        """
        return self._ssh_cfg

    @property
    def HasSSH(self) -> bool:
        """Property indicating if this MySQL source has a valid SSH configuration attached to it.

        :return: True if there is a valid SSH configuration, otherwise false.
        :rtype: bool
        """
        return (self.SSH.Host is not None and self.SSH.User is not None and self.SSH.Pass is not None)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ssh_part = f"{self.SSH.AsConnectionInfo} -> " if self.HasSSH else ""
        ret_val  = f"{self.Name} : `{ssh_part}{self.AsConnectionInfo}` ({self.Type})"
        return ret_val

    @property
    def Location(self) -> str | Path:
        return f"{self.DBHost}:{self.DBPort}"

    @property
    def Credential(self) -> CredentialConfig:
        return self._credential

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.DBUser}@{self.DBHost}:{self.DBPort}"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "MySQLConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: MySQLConfig
        """
        _db_location : URLLocationSchema  = cls._parseLocation(unparsed_elements=unparsed_elements)
        _credential  : PasswordCredential = cls._parseCredential(unparsed_elements=unparsed_elements)
        _ssh_cfg     : SSHConfig          = cls._parseSSHConfig(unparsed_elements=unparsed_elements)

        return MySQLConfig(name=name, db_location=_db_location, db_credential=_credential, ssh_cfg=_ssh_cfg, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "MySQLConfig":
        return MySQLConfig(
            name="DefaultMySQLConfig",
            db_location=cls._DEFAULT_LOCATION,
            db_credential=cls._DEFAULT_DB_CREDENTIAL,
            ssh_cfg=SSHConfig.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseLocation(unparsed_elements:Map) -> URLLocationSchema:
        return URLLocationSchema.FromDict(
            name = "DBHostLocation",
            unparsed_elements=unparsed_elements,
            key_overrides={"host" : "DB_HOST", "port" : "DB_PORT"}
        )

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> PasswordCredential:
        ret_val : PasswordCredential

        _cred_elements = MySQLConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["DB_CONFIG"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if _cred_elements:
            ret_val = PasswordCredential.FromDict(name="MySQLCredential", unparsed_elements=_cred_elements)
        else:
            _overrides = {"USER":"DB_USER", "PASS":"DB_PASS", "PW":"DB_PW"}
            ret_val = PasswordCredential.FromDict(name="MySQLCredential", unparsed_elements=unparsed_elements, key_overrides=_overrides)

        return ret_val

    @staticmethod
    def _parseSSHConfig(unparsed_elements:Map) -> SSHConfig:
        ret_val : SSHConfig

        _ssh_elements = MySQLConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SSH_CONFIG"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if _ssh_elements:
            ret_val = SSHConfig.FromDict(name="MySQLSSHConfig", unparsed_elements=_ssh_elements)
        else:
            ret_val = SSHConfig.FromDict(name="MySQLCredential", unparsed_elements=unparsed_elements)

        return ret_val

    # *** PRIVATE METHODS ***
