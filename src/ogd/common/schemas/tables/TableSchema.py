## import standard libraries
import logging
from typing import Any, Dict, List, Optional, TypeAlias
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.structures.ColumnSchema import ColumnSchema
from ogd.common.schemas.tables.structures.TableStructureSchema import TableStructureSchema
from ogd.common.schemas.tables.structures.EventTableStructureSchema import EventTableStructureSchema
from ogd.common.schemas.tables.structures.FeatureTableStructureSchema import FeatureTableStructureSchema
from ogd.common.schemas.tables.locations.TableLocationSchema import TableLocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

ColumnMapIndex   : TypeAlias = Optional[int | List[int] | Dict[str,int]]
ColumnMapElement : TypeAlias = Optional[str | List[str] | Dict[str,str]]

## @class TableStructureSchema
class TableSchema(Schema):
    """Dumb struct to hold a table structure and table location.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_COLUMNS = []

    def __init__(self, name, structure:TableStructureSchema, location:TableLocationSchema, other_elements:Optional[Map]):
        """Constructor for the TableStructureSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        # declare and initialize vars
        self._structure : TableStructureSchema = structure
        self._location  : TableLocationSchema  = location

        # after loading the file, take the stuff we need and store.
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Structure(self) -> TableStructureSchema:
        """Function to get the table's full structure schema

        :return: The table structure schema
        :rtype: TableStructureSchema
        """
        return self._structure

    @property
    def Columns(self) -> List[ColumnSchema]:
        return self._structure.Columns

    @property
    def Location(self) -> TableLocationSchema:
        return self._location

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val = "\n\n".join([
            "## Database Columns",
            f"The individual columns recorded in the data source ({self.Location}) for this game.",
            self.Structure.AsMarkdown,
            ""])
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "TableSchema":
        _structure : TableStructureSchema

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} Table Schema, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _table_type_str  : str            = str(all_elements.get('table_type'))
        _structure_elems : Dict[str, Any] = all_elements.get('structure', {})
        _location_elems  : Dict[str, Any] = all_elements.get('location', {})
        match _table_type_str.upper():
            case "EVENT":
                _structure = EventTableStructureSchema.FromDict(name=f"{name}EventStructure", all_elements=_structure_elems, logger=logger)
            case "FEATURE":
                _structure = FeatureTableStructureSchema.FromDict(name=f"{name}EventStructure", all_elements=_structure_elems, logger=logger)
        _location = TableLocationSchema.FromDict(name=f"{name}Location", all_elements=_location_elems, logger=logger)

        _used = {"table_type", "structure", "location"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return TableSchema(name=name, structure=_structure, location=_location, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "TableSchema":
        return TableSchema(
            name="DefaultTableSchema",
            structure=EventTableStructureSchema.Default(),
            location=TableLocationSchema.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
    