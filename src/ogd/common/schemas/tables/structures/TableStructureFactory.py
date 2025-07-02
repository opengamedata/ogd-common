from typing import Any, Dict

from ogd.common.schemas.tables.structures.TableStructureSchema import TableStructureSchema
from ogd.common.schemas.tables.structures.EventTableStructureSchema import EventTableStructureSchema
from ogd.common.schemas.tables.structures.FeatureTableStructureSchema import FeatureTableStructureSchema

class TableStructureFactory:
    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any])-> TableStructureSchema:
        table_type = str(all_elements.get("table_type", "NOT FOUND"))
        # _table_type       = TableType.FromString(_table_type_str) if _table_type_str is not None else TableType.EVENT
        match (table_type.upper()):
            case "EVENT":
                return EventTableStructureSchema._fromDict(name=name, unparsed_elements=all_elements)
            case "FEATURE":
                return FeatureTableStructureSchema._fromDict(name=name, unparsed_elements=all_elements)
            case _:
                raise ValueError(f"Could not generate TableStructureSchema from dictionary, table_type had invalid value {table_type}")