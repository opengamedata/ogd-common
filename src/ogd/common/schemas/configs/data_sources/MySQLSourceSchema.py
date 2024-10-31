# import standard libraries
import logging
from typing import Any, Dict, Optional, Type
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.configs.data_sources.DataSourceSchema import DataSourceSchema
from ogd.common.utils.Logger import Logger

class SSHSchema(Schema):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, host:Optional[str], user:Optional[str], pword:Optional[str], port:int, other_elements:Dict[str, Any]):
        self._host : Optional[str] = host
        self._user : Optional[str] = user
        self._pass : Optional[str] = pword
        self._port : int           = port
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Host(self) -> Optional[str]:
        return self._host

    @property
    def User(self) -> Optional[str]:
        return self._user

    @property
    def Pass(self) -> Optional[str]:
        return self._pass

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
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "SSHSchema":
        _host : Optional[str]
        _user : Optional[str]
        _pass : Optional[str]
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
        _user = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["SSH_USER"],
            parser_function=cls._parseUser,
            default_value=None
        )
        _pass = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["SSH_PW", "SSH_PASS"],
            parser_function=cls._parsePass,
            default_value=None
        )
        _port = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["SSH_PORT"],
            parser_function=cls._parsePort,
            default_value=22
        )

        _used = {"SSH_HOST", "SSH_USER", "SSH_PW", "SSH_PASS", "SSH_PORT"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return SSHSchema(name=name, host=_host, user=_user, pword=_pass, port=_port, other_elements=_leftovers)

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
    def _parseUser(user) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(user, str):
            ret_val = user
        else:
            ret_val = str(user)
            Logger.Log(f"SSH config for user was unexpected type {type(user)}, defaulting to str(user)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePass(pw) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(pw, str):
            ret_val = pw
        else:
            ret_val = str(pw)
            Logger.Log(f"SSH config for password was unexpected type {type(pw)}, defaulting to str(pw)=***.", logging.WARN)
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

class MySQLSchema(DataSourceSchema):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, db_host:str, db_port:int, db_user:str, db_pass:Optional[str], ssh_cfg:SSHSchema, other_elements:Dict[str, Any]):
        self._db_host  : str           = db_host
        self._db_port  : int           = db_port
        self._db_user  : str           = db_user
        self._db_pass  : Optional[str] = db_pass
        self._ssh_cfg  : SSHSchema     = ssh_cfg
        super().__init__(name=name, other_elements=other_elements)

    @property
    def DBHost(self) -> str:
        return self._db_host

    @property
    def DBPort(self) -> int:
        return self._db_port

    @property
    def DBUser(self) -> str:
        return self._db_user

    @property
    def DBPass(self) -> Optional[str]:
        return self._db_pass

    @property
    def SSHConfig(self) -> SSHSchema:
        return self._ssh_cfg

    @property
    def SSH(self) -> SSHSchema:
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

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ssh_part = f"{self.SSH.AsConnectionInfo} -> " if self.HasSSH else ""
        ret_val  = f"{self.Name} : `{ssh_part}{self.AsConnectionInfo}` ({self.Type})"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.DBUser}@{self.DBHost}:{self.DBPort}"
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "MySQLSchema":
        _db_host  : str
        _db_port  : int
        _db_user  : str
        _db_pass  : Optional[str]
        _ssh_cfg  : SSHSchema

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
        _db_user = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["DB_USER"],
            parser_function=cls._parseDBUser,
            default_value="UNKNOWN USER"
        )
        _db_pass = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["DB_PW", "DB_PASS"],
            parser_function=cls._parseDBPass,
            default_value=None
        )
        # Parse SSH info, if it exists. Don't notify, if it doesn't exist.
        # TODO : probably shouldn't have keys expected for SSH be hardcoded here, maybe need a way to get back what stuff it didn't use?
        _ssh_keys = {"SSH_HOST", "SSH_PORT", "SSH_USER", "SSH_PW", "SSH_PASS"}
        _ssh_elems = { key : all_elements.get(key) for key in _ssh_keys.intersection(all_elements.keys()) }
        _ssh_cfg = SSHSchema.FromDict(name=f"{name}-SSH", all_elements=_ssh_elems, logger=logger)

        _used = {"DB_HOST", "DB_PORT", "DB_USER", "DB_PW", "DB_PASS"}.union(_ssh_keys)
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return MySQLSchema(name=name, db_host=_db_host, db_port=_db_port, db_user=_db_user, db_pass=_db_pass, ssh_cfg=_ssh_cfg, other_elements=_leftovers)

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
