# import standard libraries
import logging
from pathlib import Path
from typing import Optional
# import local files
from ogd.common.configs.storage.SSHConfig import SSHConfig
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class MySQLConfig(DataStoreConfig):
    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 3306
    _DEFAULT_USER = "DEFAULT USER"
    _DEFAULT_PASS = None
    _DEFAULT_DB_CREDENTIAL = PasswordCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 db_host:str, db_port:int, db_credential:PasswordCredential, ssh_cfg:"SSHConfig",
                 # params for parent
                 store_type:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._db_host    : str                = db_host       or self._parseDBHost(unparsed_elements=unparsed_elements)
        self._db_port    : int                = db_port       or self._parseDBPort(unparsed_elements=unparsed_elements)
        self._credential : PasswordCredential = db_credential or self._parseCredential(unparsed_elements=unparsed_elements)
        self._ssh_cfg    : SSHConfig          = ssh_cfg       or self._parseSSHConfig(unparsed_elements=unparsed_elements)
        super().__init__(name=name, store_type=store_type, other_elements=other_elements)

    @property
    def DBHost(self) -> str:
        return self._db_host

    @property
    def DBPort(self) -> int:
        return self._db_port

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
    def FromDict(cls, name:str, unparsed_elements:Map)-> "MySQLConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: MySQLConfig
        """
        _db_host  : str
        _db_port  : int
        _ssh_cfg  : SSHConfig

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} MySQL Data Source config, unparsed_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        # Parse DB info
        _db_host = cls._parseDBHost(unparsed_elements=unparsed_elements)
        _db_port = cls._parseDBPort(unparsed_elements=unparsed_elements)
        _credential = cls._parseCredential(unparsed_elements=unparsed_elements)
        _ssh_cfg = cls._parseSSHConfig(unparsed_elements=unparsed_elements)

        return MySQLConfig(name=name, db_host=_db_host, db_port=_db_port, db_credential=_credential, ssh_cfg=_ssh_cfg, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "MySQLConfig":
        return MySQLConfig(
            name="DefaultMySQLConfig",
            db_host=cls._DEFAULT_HOST,
            db_port=cls._DEFAULT_PORT,
            db_credential=MySQLConfig._DEFAULT_DB_CREDENTIAL,
            ssh_cfg=SSHConfig.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseDBHost(unparsed_elements:Map) -> str:
        return MySQLConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["DB_HOST"],
            to_type=str,
            default_value=MySQLConfig._DEFAULT_HOST,
            remove_target=True
        )

    @staticmethod
    def _parseDBPort(unparsed_elements:Map) -> int:
        return MySQLConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["DB_PORT"],
            to_type=int,
            default_value=MySQLConfig._DEFAULT_HOST,
            remove_target=True
        )

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> PasswordCredential:
        ret_val : PasswordCredential

        _cred_elements = MySQLConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["DB_CREDENTIAL"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if _cred_elements:
            ret_val = PasswordCredential.FromDict(name="MySQLCredential", unparsed_elements=_cred_elements)
        else:
            ret_val = MySQLConfig._DEFAULT_DB_CREDENTIAL

        return ret_val

    @staticmethod
    def _parseSSHConfig(unparsed_elements:Map) -> SSHConfig:
        ret_val : SSHConfig

        # Parse SSH info, if it exists. Don't notify, if it doesn't exist.
        # TODO : probably shouldn't have keys expected for SSH be hardcoded here, maybe need a way to get back what stuff it didn't use?
        # TODO : In general, this should be updated to work similar to all the other parsers.
        _ssh_keys = {"SSH_HOST", "SSH_PORT", "SSH_CREDENTIAL"}
        _ssh_elems = { key : unparsed_elements.get(key) for key in _ssh_keys.intersection(unparsed_elements.keys()) }
        ret_val = SSHConfig.FromDict(name="MySQLSSHConfig", unparsed_elements=_ssh_elems)

        return ret_val

    # *** PRIVATE METHODS ***
