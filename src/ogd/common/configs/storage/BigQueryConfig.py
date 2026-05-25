# import standard libraries
from pathlib import Path
from typing import Any, Dict, Final, Optional, Self
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.KeyCredentialConfig import KeyCredential
from ogd.common.configs.locations.DatabaseLocationConfig import DatabaseLocationConfig
from ogd.common.configs.locations.FileLocationConfig import FileLocationConfig
from ogd.common.utils.typing import JSONMap, Map

class BigQueryConfig(DataStoreConfig):
    _STORE_TYPE       : Final[str] = "BIGQUERY"
    _DEFAULT_LOCATION : Final[DatabaseLocationConfig] = DatabaseLocationConfig(
        name="DefaultBQLocation",
        database_name="wcer-field-day-ogd-1798",
        table_name=None,
        other_elements=None
    )
    _DEFAULT_CREDENTIAL : Final[KeyCredential] = KeyCredential(
        name="DefaultBQKeyCredential",
        location=FileLocationConfig(name="DefaultBQKeyFile", folder_path=Path("./config/"), filename="ogd.json"),
    )

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 location:Optional[DatabaseLocationConfig | Map | str],
                 credential:Optional[KeyCredential | Map | str],
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the `BigQueryConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "SOURCE_TYPE" : "BIGQUERY",
            "PROJECT_ID" : "someprojectid",
            "PROJECT_KEY" : {
                "KEY" : "key.txt",
                "PATH" : "./"
            }
        }
        ```

        :param name: _description_
        :type name: str
        :param location: _description_
        :type location: Optional[DatabaseLocationConfig]
        :param credential: _description_
        :type credential: Optional[KeyCredential]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        fallbacks : Map = other_elements or {}

        self._location   : DatabaseLocationConfig = self._toLocation(location=location, fallbacks=fallbacks, schema_name=name)
        self._credential : KeyCredential          = self._toCredential(credential=credential, fallbacks=fallbacks, schema_name=name)

        super().__init__(name=name, store_type=self._STORE_TYPE, other_elements=fallbacks)

    @property
    def Location(self) -> DatabaseLocationConfig:
        """The Project ID for the BigQuery source

        :return: _description_
        :rtype: str
        """
        return self._location

    @property
    def Credential(self) -> KeyCredential:
        return self._credential

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.Location.Location}"
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: `{self.AsConnectionInfo}` ({self.Type})"
        return ret_val

    @property
    def AsDict(self) -> JSONMap:
        return {
            "SOURCE_TYPE":"BIGQUERY",
            "PROJECT_ID":self.Location.AsDict,
            "PROJECT_KEY":self.Credential.AsDict
        }

    @classmethod
    def Default(cls) -> "BigQueryConfig":
        return BigQueryConfig(
            name="DefaultBigQueryConfig",
            location=cls._DEFAULT_LOCATION,
            credential=KeyCredential.Default(),
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None) -> "BigQueryConfig":
        """Create a BigQuery Configuration from a dict.

        Expects dictionary to have the following form:
        ```json
        {
            "SOURCE_TYPE" : "BIGQUERY",
            "PROJECT_ID" : "someprojectid",
            "PROJECT_KEY" : {
                "FILE" : "key.txt",
                "PATH" : "./"
            }
        }
        ```

        Optionally, use "DATASET_ID" or "database" in place of "PROJECT_ID" key.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: BigQueryConfig
        """
        return BigQueryConfig(name=name, location=None, credential=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toLocation(location:Optional[DatabaseLocationConfig | Map | str], fallbacks:Map, schema_name:Optional[str]=None) -> DatabaseLocationConfig:
        ret_val : DatabaseLocationConfig
        if isinstance(location, DatabaseLocationConfig):
            ret_val = location
        elif isinstance(location, dict):
            ret_val = DatabaseLocationConfig.FromDict(name=f"{schema_name}DatabaseLocation", unparsed_elements=location)
        elif isinstance(location, str):
            ret_val = DatabaseLocationConfig(name=f"{schema_name}DatabaseLocation", database_name=location, table_name=None)
        else:
            ret_val = BigQueryConfig._parseLocation(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _toCredential(credential:Optional[KeyCredential | Map | str], fallbacks:Map, schema_name:Optional[str]=None) -> KeyCredential:
        ret_val : KeyCredential
        if isinstance(credential, KeyCredential):
            ret_val = credential
        elif isinstance(credential, dict):
            ret_val = KeyCredential.FromDict(name=f"{schema_name}Credential", unparsed_elements=credential)
        elif isinstance(credential, str):
            ret_val = KeyCredential(name=f"{schema_name}Credential", location=credential)
        else:
            ret_val = BigQueryConfig._parseCredential(unparsed_elements=fallbacks, schema_name=schema_name)
        return ret_val

    @staticmethod
    def _parseLocation(unparsed_elements:Map, schema_name:Optional[str]=None) -> DatabaseLocationConfig:
        ret_val : DatabaseLocationConfig

        # First check for project ID or dataset ID given directly
        project_id = BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_ID", "DATASET_ID"],
            to_type=str,
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )
        # If we found it, use to construct
        if project_id:
            ret_val = DatabaseLocationConfig(name="BigQueryLocation", database_name=project_id, table_name=None, other_elements={})
        # Else, have the class look for whatever key it's expecting.
        else:
            ret_val = DatabaseLocationConfig.FromDict(name="BigQueryLocation", unparsed_elements=unparsed_elements)
        
        return ret_val

    @staticmethod
    def _parseCredential(unparsed_elements:Map, schema_name:Optional[str]=None) -> KeyCredential:
        ret_val : KeyCredential

        raw_credential = BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_KEY"],
            to_type=[dict, str],
            default_value=BigQueryConfig._DEFAULT_CREDENTIAL,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_credential, dict):
            ret_val = KeyCredential.FromDict(name=f"{schema_name}KeyCredential", unparsed_elements=raw_credential)
        elif isinstance(raw_credential, str):
            ret_val = KeyCredential(
                name=f"{schema_name}ConfigCredential",
                location=FileLocationConfig.FromDict(name=f"{schema_name}CredentialLocation",
                unparsed_elements={"file":raw_credential}), other_elements=None
            )
        return ret_val

    # *** PRIVATE METHODS ***

