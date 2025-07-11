## import standard libraries
import logging
from typing import Any, Dict, Optional
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class TableStructureSchema
class TableLocationSchema(Schema):

    _DEFAULT_TABLE_NAME = "DEFAULT TABLE"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, table_name:str, other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}

        self._table_name = table_name or self._parseTableName(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def TableName(self) -> str:
        return self._table_name

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.TableName}"
        return ret_val

    @classmethod
    def Default(cls) -> "TableLocationSchema":
        return TableLocationSchema(
            name="DefaultTableLocation",
            table_name=cls._DEFAULT_TABLE_NAME,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "TableLocationSchema":
        """Create a TableLocationSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: GameSourceSchema
        """
        _table_name    : str = cls._parseTableName(unparsed_elements=unparsed_elements)

        _used = {"table"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return TableLocationSchema(name=name, table_name=_table_name, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseTableName(unparsed_elements:Map) -> str:
        return TableLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["table"],
            to_type=str,
            default_value=TableLocationSchema._DEFAULT_TABLE_NAME,
            remove_target=True
        )
