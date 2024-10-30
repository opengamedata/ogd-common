# import standard libraries
import abc
import logging
from typing import Any, Dict
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class DataSourceSchema(Schema):

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def AsConnectionInfo(self) -> str:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, other_elements:Dict[str, Any]):
        self._db_type : str
        if not isinstance(other_elements, dict):
            other_elements = {}
            Logger.Log(f"For {name} Data Source config, other_elements was not a dict, defaulting to empty dict", logging.WARN)
        # Parse DB info
        self._db_type = DataSourceSchema.ElementFromDict(all_elements=other_elements, logger=None,
            element_names=["DB_TYPE"],
            parser_function=DataSourceSchema._parseDBType,
            default_value="UNKNOWN"
        )

        _used = {"DB_TYPE"}
        _leftovers = { key : val for key,val in other_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Type(self) -> str:
        """The type of source indicated by the data source schema.

        This includes but is not limited to "FIREBASE", "BIGQUERY", and "MySQL"

        :return: A string describing the type of the data source
        :rtype: str
        """
        return self._db_type

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseDBType(db_type) -> str:
        ret_val : str
        if isinstance(db_type, str):
            ret_val = db_type
        else:
            ret_val = str(db_type)
            Logger.Log(f"Data Source DB type was unexpected type {type(db_type)}, defaulting to str(db_type)={ret_val}.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
