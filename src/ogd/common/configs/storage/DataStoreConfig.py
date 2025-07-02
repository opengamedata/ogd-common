# import standard libraries
import abc
from pathlib import Path
from typing import Optional
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.utils.typing import Map


class DataStoreConfig(Config):
    """Dumb struct to contain data pertaining to a data source, which a StorageConnector can connect to.

    Every source has:
    - A named "type" to inform what StorageConnector should be instantiated
    - A config "name" for use within ogd software for identifying a particular data source config
    - A resource "location" for use by the StorageConnector (such as a filename, cloud project name, or database host)
    """

    _DEFAULT_TYPE = "UNKNOWN STORE TYPE"

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Location(self) -> str | Path:
        pass

    @property
    @abc.abstractmethod
    def Credential(self) -> CredentialConfig:
        pass

    @property
    @abc.abstractmethod
    def AsConnectionInfo(self) -> str:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, store_type:Optional[str], other_elements:Optional[Map]=None):
        unparsed_elements : Map = {key.upper() : val for key, val in other_elements.items()} if other_elements else {}

        self._store_type : str = store_type or self._parseStoreType(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=unparsed_elements)

    @property
    def Type(self) -> str:
        """The type of source indicated by the data source schema.

        This includes but is not limited to "FIREBASE", "BIGQUERY", and "MySQL".
        It is used primarily to indicate that data store class the config is compatible with;
        may be subject to replacement/removal at some point.

        :return: A string describing the type of the data source
        :rtype: str
        """
        return self._store_type

    # *** PUBLIC STATICS ***


    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseStoreType(unparsed_elements:Map) -> str:
        return DataStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SOURCE_TYPE", "DB_TYPE"],
            to_type=str,
            default_value=DataStoreConfig._DEFAULT_TYPE,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
