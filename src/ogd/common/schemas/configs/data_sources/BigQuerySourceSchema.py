# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Type
# import local files
from ogd.common.schemas.configs.data_sources.DataSourceSchema import DataSourceSchema
from ogd.common.utils.Logger import Logger

class BigQuerySchema(DataSourceSchema):
    _DEFAULT_PROJECT_ID = "wcer-field-day-ogd-1798"
    _DEFAULT_CREDENTIAL = "./config/ogd.json"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, project_id:str, credential:Optional[str], other_elements:Dict[str, Any]):
        self._project_id : str           = project_id
        self._credential : Optional[str] = credential

        super().__init__(name=name, other_elements=other_elements)

    @property
    def ProjectID(self) -> str:
        return self._project_id

    @property
    def Credential(self) -> Optional[str]:
        return self._credential

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.ProjectID}"
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: `{self.AsConnectionInfo}` ({self.Type})"
        return ret_val

    @classmethod
    def Default(cls) -> "BigQuerySchema":
        return BigQuerySchema(
            name="DefaultBigQuerySchema",
            project_id=BigQuerySchema._DEFAULT_PROJECT_ID,
            credential=BigQuerySchema._DEFAULT_CREDENTIAL,
            other_elements={}
        )

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]) -> "BigQuerySchema":
        _project_id : str
        _credential : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} BigQuery Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        _project_id = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["PROJECT_ID", "DATASET_ID"],
            parser_function=cls._parseProjectID,
            default_value=BigQuerySchema._DEFAULT_PROJECT_ID
        )
        _credential = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["PROJECT_KEY"],
            parser_function=cls._parseCredential,
            default_value=BigQuerySchema._DEFAULT_CREDENTIAL
        )

        _used = {"PROJECT_ID", "DATASET_ID", "PROJECT_KEY"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return BigQuerySchema(name=name, project_id=_project_id, credential=_credential, other_elements=_leftovers)

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

