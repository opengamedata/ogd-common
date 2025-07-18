# import standard libraries
from pathlib import Path
from typing import Dict, Optional
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.KeyCredentialConfig import KeyCredential
from ogd.common.schemas.locations.DatabaseLocationSchema import DatabaseLocationSchema
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.utils.typing import Map

class BigQueryConfig(DataStoreConfig):
    _DEFAULT_LOCATION = DatabaseLocationSchema(
        name="DefaultBQLocation",
        database_name="wcer-field-day-ogd-1798",
        table_name=None,
        other_elements=None
    )
    _DEFAULT_CREDENTIAL = KeyCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 location:DatabaseLocationSchema, credential:KeyCredential,
                 # params for parent
                 store_type:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._location   : DatabaseLocationSchema  = location if location else BigQueryConfig._parseLocation(unparsed_elements=unparsed_elements)
        self._credential : KeyCredential           = credential or BigQueryConfig._parseCredential(unparsed_elements=unparsed_elements)

        super().__init__(name=name, store_type=store_type, other_elements=unparsed_elements)

    @property
    def Location(self) -> DatabaseLocationSchema:
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

    @classmethod
    def Default(cls) -> "BigQueryConfig":
        return BigQueryConfig(
            name="DefaultBigQueryConfig",
            location=cls._DEFAULT_LOCATION,
            credential=KeyCredential.Default(),
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None) -> "BigQueryConfig":
        """Create a BigQuery Configuration from a dict.

        Expects dictionary to have the following form:
        ```json
        {
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
        _project_id : DatabaseLocationSchema  = cls._parseLocation(unparsed_elements=unparsed_elements)
        _credential : Optional[KeyCredential] = cls._parseCredential(unparsed_elements=unparsed_elements)

        _used = {"PROJECT_ID", "DATASET_ID", "PROJECT_KEY"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return BigQueryConfig(name=name, location=_project_id, credential=_credential, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseLocation(unparsed_elements:Map) -> DatabaseLocationSchema:
        ret_val : DatabaseLocationSchema

        # First check for project ID or dataset ID given directly
        project_id = BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_ID", "DATASET_ID"],
            to_type=str,
            default_value=None,
            remove_target=True
        )
        # If we found it, use to construct
        if project_id:
            ret_val = DatabaseLocationSchema(name="BigQueryLocation", database_name=project_id, table_name=None, other_elements={})
        # Else, have the class look for whatever key it's expecting.
        else:
            ret_val = DatabaseLocationSchema.FromDict(name="BigQueryLocation", unparsed_elements=unparsed_elements)
        
        return ret_val

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> KeyCredential:
        ret_val : KeyCredential

        raw_credential = BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_KEY"],
            to_type=[dict, str],
            default_value=BigQueryConfig._DEFAULT_CREDENTIAL,
            remove_target=True
        )
        if isinstance(raw_credential, dict):
            ret_val = KeyCredential.FromDict(name="KeyCredential", unparsed_elements=raw_credential)
        elif isinstance(raw_credential, str):
            ret_val = KeyCredential(name="BigQueryConfigCredential", location=FileLocationSchema.FromDict(name="BQCredentialLocation", unparsed_elements={"file":raw_credential}), other_elements=None)
        return ret_val

    # *** PRIVATE METHODS ***

