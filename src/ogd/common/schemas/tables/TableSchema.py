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

## @class TableSchema
class TableSchema(Schema):
    """Dumb struct to hold a table structure and table location.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_TABLE_TYPE = "EVENT"
    _DEFAULT_STRUCTURE = {}
    _DEFAULT_LOCATION = {}

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
        unparsed_elements = other_elements or {}
        _table_type = self._parseTableType(unparsed_elements=unparsed_elements)
        self._structure : TableStructureSchema = structure or self._parseStructure(name=f"{name}Structure", table_type=_table_type, unparsed_elements=unparsed_elements)
        self._location  : TableLocationSchema  = location  or self._parseLocation(name=f"{name}Location", unparsed_elements=unparsed_elements)

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
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "TableSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: TableSchema
        """
        _structure : TableStructureSchema

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} Table Schema, unparsed_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _table_type_str  = cls._parseTableType(unparsed_elements=unparsed_elements)
        _structure       = cls._parseStructure(name=name, table_type=_table_type_str, unparsed_elements=unparsed_elements)
        _location        = cls._parseLocation(name=name, unparsed_elements=unparsed_elements)

        _used = {"table_type", "structure", "location"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
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

    @staticmethod
    def _parseTableType(unparsed_elements:Map) -> str:
        return TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["table_type"],
            to_type=str,
            default_value=TableSchema._DEFAULT_TABLE_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseStructure(name:str, table_type:str, unparsed_elements:Map) -> TableStructureSchema:
        ret_val : TableStructureSchema

        _structure = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["structure"],
            to_type=dict,
            default_value=TableSchema._DEFAULT_STRUCTURE,
            remove_target=True
        )
        match table_type.upper():
            case "EVENT":
                ret_val = EventTableStructureSchema._fromDict(name=f"{name}EventStructure", unparsed_elements=_structure)
            case "FEATURE":
                ret_val = FeatureTableStructureSchema._fromDict(name=f"{name}EventStructure", unparsed_elements=_structure)
        
        return ret_val

    @staticmethod
    def _parseLocation(name:str, unparsed_elements:Map) -> TableLocationSchema:
        ret_val : TableLocationSchema

        _location = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["location"],
            to_type=dict,
            default_value=TableSchema._DEFAULT_LOCATION,
            remove_target=True
        )
        ret_val = TableLocationSchema._fromDict(name=f"{name}Location", unparsed_elements=_location)

        return ret_val

    # *** PRIVATE METHODS ***
    