# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.utils.Logger import Logger

class SSHConfig(Schema):
    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 22

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, ssh_host:Optional[str], ssh_credential:PasswordCredential, ssh_port:int, other_elements:Dict[str, Any]):
        self._host       : Optional[str]      = ssh_host
        self._credential : PasswordCredential = ssh_credential
        self._port       : int                = ssh_port
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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "SSHConfig":
        _host : Optional[str]
        _port : int

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} MySQL Source config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _host = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["SSH_HOST"],
            parser_function=cls._parseHost,
            default_value=None # TODO : use class default
        )
        _port = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["SSH_PORT"],
            parser_function=cls._parsePort,
            default_value=22
        )
        # TODO : determine whether this could work as own parser function.
        _credential = PasswordCredential.FromDict(name=f"{name}Credential",
                                                  all_elements=all_elements.get("SSH_CREDENTIAL", {}),
                                                  logger=logger
        )

        _used = {"SSH_HOST", "SSH_PORT", "SSH_CREDENTIAL"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return SSHConfig(name=name, ssh_host=_host, ssh_credential=_credential, ssh_port=_port, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "SSHConfig":
        return SSHConfig(
            name="DefaultSSHConfig",
            ssh_host=cls._DEFAULT_HOST,
            ssh_credential=PasswordCredential.Default(),
            ssh_port=cls._DEFAULT_PORT,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseHost(host) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(host, str):
            ret_val = host
        else:
            ret_val = str(host)
            Logger.Log(f"SSH config for host was unexpected type {type(host)}, defaulting to str(host)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePort(port) -> int:
        ret_val : int
        if isinstance(port, int):
            ret_val = port
        elif isinstance(port, str):
            ret_val = int(port)
        else:
            ret_val = int(port)
            Logger.Log(f"SSH config for port was unexpected type {type(port)}, defaulting to int(port)={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***

class MySQLConfig(DataStoreConfig):
    _DEFAULT_HOST = "127.0.0.1"
    _DEFAULT_PORT = 22
    _DEFAULT_USER = "DEFAULT USER"
    _DEFAULT_PASS = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, db_host:str, db_port:int, db_credential:PasswordCredential, ssh_cfg:"SSHConfig", other_elements:Dict[str, Any]):
        self._db_host    : str                = db_host
        self._db_port    : int                = db_port
        self._credential : PasswordCredential = db_credential
        self._ssh_cfg    : SSHConfig          = ssh_cfg
        super().__init__(name=name, other_elements=other_elements)

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
    def SSHConfig(self) -> SSHConfig:
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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "MySQLConfig":
        _db_host  : str
        _db_port  : int
        _ssh_cfg  : SSHConfig

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} MySQL Data Source config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        # Parse DB info
        _db_host = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["DB_HOST"],
            parser_function=cls._parseDBHost,
            default_value="UNKNOWN DB HOST"
        )
        _db_port = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["DB_PORT"],
            parser_function=cls._parseDBPort,
            default_value=3306
        )
        # TODO : determine whether this could work as own parser function.
        _credential = PasswordCredential.FromDict(name=f"{name}Credential",
                                                  all_elements=all_elements.get("DB_CREDENTIAL", {}),
                                                  logger=logger
        )
        # Parse SSH info, if it exists. Don't notify, if it doesn't exist.
        # TODO : probably shouldn't have keys expected for SSH be hardcoded here, maybe need a way to get back what stuff it didn't use?
        _ssh_keys = {"SSH_HOST", "SSH_PORT", "SSH_CREDENTIAL"}
        _ssh_elems = { key : all_elements.get(key) for key in _ssh_keys.intersection(all_elements.keys()) }
        _ssh_cfg = SSHConfig.FromDict(name=f"{name}-SSH", all_elements=_ssh_elems, logger=logger)

        _used = {"DB_HOST", "DB_PORT", "DB_CREDENTIAL"}.union(_ssh_keys)
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return MySQLConfig(name=name, db_host=_db_host, db_port=_db_port, db_credential=_credential, ssh_cfg=_ssh_cfg, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "MySQLConfig":
        return MySQLConfig(
            name="DefaultMySQLConfig",
            db_host=cls._DEFAULT_HOST,
            db_port=cls._DEFAULT_PORT,
            db_credential=PasswordCredential.Default(),
            ssh_cfg=SSHConfig.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseDBHost(db_host) -> str:
        ret_val : str
        if isinstance(db_host, str):
            ret_val = db_host
        else:
            ret_val = str(db_host)
            Logger.Log(f"MySQL Data Source DB host was unexpected type {type(db_host)}, defaulting to str(db_host)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDBPort(db_port) -> int:
        ret_val : int
        if isinstance(db_port, int):
            ret_val = db_port
        else:
            ret_val = int(db_port)
            Logger.Log(f"MySQL Data Source DB port was unexpected type {type(db_port)}, defaulting to int(db_port)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDBUser(db_user) -> str:
        ret_val : str
        if isinstance(db_user, str):
            ret_val = db_user
        else:
            ret_val = str(db_user)
            Logger.Log(f"MySQL Data Source DB username was unexpected type {type(db_user)}, defaulting to str(db_user)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDBPass(db_pass) -> str:
        ret_val : str
        if isinstance(db_pass, str):
            ret_val = db_pass
        else:
            ret_val = str(db_pass)
            Logger.Log(f"MySQL Data Source DB password was unexpected type, defaulting to str(db_pass)=***.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
