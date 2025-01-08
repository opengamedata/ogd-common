## import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, TypeAlias
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

## @class TableStructureSchema
class TableLocationSchema(Schema):
    def __init__(self, name:str, table_name:str, other_elements:Optional[Map]):
        self._table_name = table_name
        super().__init__(name=name, other_elements=other_elements)

    @property
    def TableName(self) -> str:
        return self._table_name