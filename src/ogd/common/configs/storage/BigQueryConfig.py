# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Type
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.utils.Logger import Logger

class BigQueryConfig(DataStoreConfig):
    _DEFAULT_PROJECT_ID = "wcer-field-day-ogd-1798"
    _DEFAULT_CREDENTIAL = "./config/ogd.json"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, project_id:str, credential:Optional[str], other_elements:Dict[str, Any]):
        self._project_id : str           = project_id
        self._credential : Optional[str] = credential

        super().__init__(name=name, other_elements=other_elements)

    @property
    def Location(self) -> str:
        """The Project ID for the BigQuery source

        :return: _description_
        :rtype: str
        """
        return self._project_id

    @property
    def Credential(self) -> Optional[str]:
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
            credential=cls._DEFAULT_CREDENTIAL,
            other_elements={}
        )

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]) -> "BigQueryConfig":
        _project_id : str
        _credential : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} BigQuery Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        _project_id = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["PROJECT_ID", "DATASET_ID"],
            to_type=cls._parseProjectID,
            default_value=BigQueryConfig._DEFAULT_PROJECT_ID
        )
        _credential = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["PROJECT_KEY"],
            to_type=cls._parseCredential,
            default_value=BigQueryConfig._DEFAULT_CREDENTIAL
        )

        _used = {"PROJECT_ID", "DATASET_ID", "PROJECT_KEY"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return BigQueryConfig(name=name, project_id=_project_id, credential=_credential, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseProjectID(project_id) -> str:
        ret_val : str
        if isinstance(project_id, str):
            ret_val = project_id
        else:
            ret_val = str(project_id)
            Logger.Log(f"Data Source project ID was unexpected type {type(project_id)}, defaulting to str(project_id)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseCredential(credential) -> str:
        ret_val : str
        if isinstance(credential, str):
            ret_val = credential
        else:
            ret_val = str(credential)
            Logger.Log(f"Game Source credential type was unexpected type {type(credential)}, defaulting to str(credential)={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***

