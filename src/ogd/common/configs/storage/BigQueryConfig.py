# import standard libraries
import logging
from typing import Optional
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.KeyCredentialConfig import KeyCredential
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class BigQueryConfig(DataStoreConfig):
    _DEFAULT_PROJECT_ID = "wcer-field-day-ogd-1798"
    _DEFAULT_CREDENTIAL = KeyCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 project_id:str, credential:KeyCredential,
                 # params for parent
                 store_type:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._project_id : str           = project_id or BigQueryConfig._parseProjectID(unparsed_elements=unparsed_elements)
        self._credential : KeyCredential = credential or BigQueryConfig._parseCredential(unparsed_elements=unparsed_elements)

        super().__init__(name=name, store_type=store_type, other_elements=unparsed_elements)

    @property
    def Location(self) -> str:
        """The Project ID for the BigQuery source

        :return: _description_
        :rtype: str
        """
        return self._project_id

    @property
    def Credential(self) -> KeyCredential:
        return self._credential

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.Location}"
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
            project_id=cls._DEFAULT_PROJECT_ID,
            credential=KeyCredential.Default(),
            other_elements={}
        )

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Map) -> "BigQueryConfig":
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

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: BigQueryConfig
        """
        _project_id : str
        _credential : Optional[KeyCredential]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            Logger.Log(f"For {name} BigQuery Source config, unparsed_elements was not a dict, defaulting to empty dict", logging.WARN)
        _project_id = cls._parseProjectID(unparsed_elements=unparsed_elements)
        _credential = cls._parseCredential(unparsed_elements=unparsed_elements)

        _used = {"PROJECT_ID", "DATASET_ID", "PROJECT_KEY"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return BigQueryConfig(name=name, project_id=_project_id, credential=_credential, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseProjectID(unparsed_elements:Map) -> str:
        return BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_ID", "DATASET_ID"],
            to_type=str,
            default_value=BigQueryConfig._DEFAULT_PROJECT_ID,
            remove_target=True
        )

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> KeyCredential:
        ret_val : KeyCredential

        raw_credential = BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_KEY"],
            to_type=dict,
            default_value=BigQueryConfig._DEFAULT_CREDENTIAL,
            remove_target=True
        )
        ret_val = KeyCredential.FromDict(name="KeyCredential", unparsed_elements=raw_credential)
        return ret_val

    # *** PRIVATE METHODS ***

