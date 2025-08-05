import logging
import traceback
from typing import Final, Optional, Tuple
# 3rd-party imports
import sshtunnel
from mysql.connector import connection, cursor
# import locals
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.configs.storage.MySQLConfig import MySQLConfig
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

class MySQLConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:MySQLConfig):
        self._config = config
        self._tunnel : Optional[sshtunnel.SSHTunnelForwarder] = None
        self._connection : Optional[connection.MySQLConnection] = None
        super().__init__()

    @property
    def Connection(self) -> Optional[connection.MySQLConnection]:
        return self._connection

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def StoreConfig(self) -> MySQLConfig:
        return self._config

    def _open(self, force_reopen: bool = False) -> bool:
        """
        Function to set up a connection to a database, via an ssh tunnel if available.

        :param db_settings: A dictionary mapping names of database parameters to values.
        :type db_settings: Dict[str,Any]
        :param ssh_settings: A dictionary mapping names of ssh parameters to values, or None if no ssh connection is desired., defaults to None
        :type ssh_settings: Optional[Dict[str,Any]], optional
        :return: A tuple consisting of the tunnel and database connection, respectively.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        Logger.Log("Preparing database connection...", logging.DEBUG)
        if force_reopen and self.Connection is not None:
            Logger.Log("Forced prior DB connection to close", logging.INFO)
            self.Connection.close()
        if self.StoreConfig is not None and isinstance(self.StoreConfig, MySQLConfig):
            if self.StoreConfig.HasSSH:
                Logger.Log(f"Preparing to connect to MySQL via SSH, on host {self.StoreConfig.SSH.Host}", level=logging.DEBUG)
                if (self.StoreConfig.SSH.Host is not None and self.StoreConfig.SSH.Host != ""
                and self.StoreConfig.SSH.User is not None and self.StoreConfig.SSH.User != ""
                and self.StoreConfig.SSH.Pass is not None and self.StoreConfig.SSH.Pass != ""):
                    self._tunnel,self._connection = self._connectToMySQLviaSSH(sql=self.StoreConfig)
                else:
                    Logger.Log(f"SSH login had empty data, preparing to connect to MySQL directly instead, on host {self.StoreConfig.DBHost}", level=logging.DEBUG)
                    self._connection = self._connectToMySQL(login=self.StoreConfig)
            else:
                Logger.Log(f"Preparing to connect to MySQL directly, on host {self.StoreConfig.DBHost}", level=logging.DEBUG)
                self._connection = self._connectToMySQL(login=self.StoreConfig)
            Logger.Log("Done preparing database connection.", logging.DEBUG)
        else:
            Logger.Log("Unable to connect to MySQL, game source schema does not have a valid MySQL config!", level=logging.ERROR)

        return self.Connection is not None and self.Connection.is_connected()

    def _close(self) -> bool:
        if self.Connection is not None:
            self.Connection.close()
            Logger.Log("Closed MySQL database connection", logging.DEBUG)
        else:
            Logger.Log("No MySQL database to close.", logging.DEBUG)
        if self._tunnel is not None:
            self._tunnel.stop()
            Logger.Log("Stopped MySQL tunnel connection", logging.DEBUG)
        else:
            Logger.Log("No MySQL tunnel to stop", logging.DEBUG)
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    @property
    def IsOpen(self) -> bool:
        """Overridden version of IsOpen function, checks that BigQueryInterface client has been initialized.

        :return: True if the interface is open, else False
        :rtype: bool
        """
        return True if (super().IsOpen and self.Connection is not None and self.Connection.is_connected()) else False

    # *** PRIVATE STATICS ***

    # Function to help connect to a mySQL server.
    @staticmethod
    def _connectToMySQL(login:MySQLConfig) -> Optional[connection.MySQLConnection]:
        """Function to help connect to a mySQL server.

        Simply tries to make a connection, and prints an error in case of failure.
        :param login: A SQLLogin object with the data needed to log into MySQL.
        :type login: SQLLogin
        :return: If successful, a MySQLConnection object, otherwise None.
        :rtype: Optional[connection.MySQLConnection]
        """
        try:
            Logger.Log(f"Connecting to SQL (no SSH) at {login.AsConnectionInfo}...", logging.DEBUG)
            db_conn = connection.MySQLConnection(host     = login.DBHost,    port    = login.DBPort,
                                                 user     = login.DBUser,    password= login.DBPass,
                                                 charset = 'utf8')
            Logger.Log(f"Connected.", logging.DEBUG)
            return db_conn
        #except MySQLdb.connections.Error as err:
        except Exception as err:
            msg = f"""Could not connect to the MySql database.
            Login info: {login.AsConnectionInfo} w/port type={type(login.DBPort)}.
            Full error: {type(err)} {str(err)}"""
            Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            return None

    ## Function to help connect to a mySQL server over SSH.
    @staticmethod
    def _connectToMySQLviaSSH(sql:MySQLConfig) -> Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]:
        """Function to help connect to a mySQL server over SSH.

        Simply tries to make a connection, and prints an error in case of failure.
        :param sql: A SQLLogin object with the data needed to log into MySQL.
        :type sql: SQLLogin
        :param ssh: An SSHLogin object with the data needed to log into MySQL.
        :type ssh: SSHLogin
        :return: An open connection to the database if successful, otherwise None.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        tunnel    : Optional[sshtunnel.SSHTunnelForwarder] = None
        db_conn   : Optional[connection.MySQLConnection] = None
        MAX_TRIES : Final[int] = 5
        tries : int = 0
        connected_ssh : bool = False

        # First, connect to SSH
        while connected_ssh == False and tries < MAX_TRIES:
            if tries > 0:
                Logger.Log("Re-attempting to connect to SSH.", logging.INFO)
            try:
                Logger.Log(f"Connecting to SSH at {sql.SSHConf.AsConnectionInfo}...", logging.DEBUG)
                tunnel = sshtunnel.SSHTunnelForwarder(
                    (sql.SSH.Host, sql.SSH.Port), ssh_username=sql.SSH.User, ssh_password=sql.SSH.Pass,
                    remote_bind_address=(sql.DBHost, sql.DBPort), logger=Logger.std_logger
                )
                tunnel.start()
                connected_ssh = True
                Logger.Log(f"Connected.", logging.DEBUG)
            except Exception as err:
                msg = f"Could not connect via SSH: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.Print(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                tries = tries + 1
        if connected_ssh == True and tunnel is not None:
            # Then, connect to MySQL
            try:
                Logger.Log(f"Connecting to SQL (via SSH) at {sql.DBUser}@{sql.DBHost}:{tunnel.local_bind_port}...", logging.DEBUG)
                db_conn = connection.MySQLConnection(host     = sql.DBHost,    port    = tunnel.local_bind_port,
                                                     user     = sql.DBUser,    password= sql.DBPass,
                                                     charset ='utf8')
                Logger.Log(f"Connected", logging.DEBUG)
                return (tunnel, db_conn)
            except Exception as err:
                msg = f"Could not connect to the MySql database: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.Print(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                if tunnel is not None:
                    tunnel.stop()
                return (None, None)
        else:
            return (None, None)



    # *** PRIVATE METHODS ***
