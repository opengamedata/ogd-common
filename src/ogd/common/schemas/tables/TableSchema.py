## import standard libraries
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.schemas.tables.TableStructureSchema import TableStructureSchema
from ogd.common.schemas.tables.EventTableStructureSchema import EventTableStructureSchema
from ogd.common.schemas.tables.FeatureTableStructureSchema import FeatureTableStructureSchema
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.schemas.locations.DatabaseLocationSchema import DatabaseLocationSchema
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
    _DEFAULT_LOCATION_TYPE = "FILE"
    _DEFAULT_LOCATION = {}

    def __init__(self, name, structure:TableStructureSchema, location:LocationSchema, other_elements:Optional[Map]=None):
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
        unparsed_elements : Map = other_elements or {}
        _table_type = self._parseTableType(unparsed_elements=unparsed_elements)
        self._structure : TableStructureSchema = structure or self._parseStructure(name=f"{name}Structure", table_type=_table_type, unparsed_elements=unparsed_elements)
        _location_type = self._parseLocationType(unparsed_elements=unparsed_elements)
        self._location  : LocationSchema  = location  or self._parseLocation(name=f"{name}Location", location_type=_location_type, unparsed_elements=unparsed_elements)

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
    def Location(self) -> LocationSchema:
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
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "TableSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: TableSchema
        """
        _table_type_str : str                  = cls._parseTableType(unparsed_elements=unparsed_elements)
        _structure      : TableStructureSchema = cls._parseStructure(name=name, table_type=_table_type_str, unparsed_elements=unparsed_elements)
        _loc_type_str   : str                  = cls._parseLocationType(unparsed_elements=unparsed_elements)
        _location       : LocationSchema       = cls._parseLocation(name=name, location_type=_loc_type_str, unparsed_elements=unparsed_elements)

        _used = {"table_type", "structure", "location_type", "location"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return TableSchema(name=name, structure=_structure, location=_location, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "TableSchema":
        return TableSchema(
            name="DefaultTableSchema",
            structure=EventTableStructureSchema.Default(),
            location=FileLocationSchema.Default(),
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseTableType(unparsed_elements:Map, keys:List[str]=["table_type"]) -> str:
        return TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=keys,
            to_type=str,
            default_value=TableSchema._DEFAULT_TABLE_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseStructure(name:str, table_type:str, unparsed_elements:Map, keys:List[str]=["structure"]) -> TableStructureSchema:
        ret_val : TableStructureSchema

        _structure = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=keys,
            to_type=[Path, dict], # check first if we got a string that parses to a path for the file, otherwise assume whole structure is given.
            default_value=TableSchema._DEFAULT_STRUCTURE,
            remove_target=True
        )
        match table_type.upper():
            case "EVENT":
                ret_val =  EventTableStructureSchema.FromFile(schema_name=_structure.name, schema_path=_structure.parent) \
                        if type(_structure) == Path else \
                           EventTableStructureSchema.FromDict(name=f"{name}EventStructure", unparsed_elements=_structure)
                          
            case "FEATURE":
                ret_val =  FeatureTableStructureSchema.FromFile(schema_name=_structure.name, schema_path=_structure.parent) \
                        if type(_structure) == Path else \
                           FeatureTableStructureSchema.FromDict(name=f"{name}EventStructure", unparsed_elements=_structure)
                
        
        return ret_val

    @staticmethod
    def _parseLocationType(unparsed_elements:Map, keys:List[str]=["location_type"]) -> str:
        return TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=keys,
            to_type=str,
            default_value=TableSchema._DEFAULT_LOCATION_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseLocation(name:str, location_type:str, unparsed_elements:Map, keys:List[str]=["location"]) -> LocationSchema:
        ret_val : LocationSchema

        _location = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=keys,
            to_type=dict,
            default_value=TableSchema._DEFAULT_LOCATION,
            remove_target=True
        )
        match location_type.upper():
            case "FILE":
                ret_val = FileLocationSchema.FromDict(name=f"{name}Location", unparsed_elements=_location)
            case "URL":
                ret_val = URLLocationSchema.FromDict(name=f"{name}Location", unparsed_elements=_location)
            case "DB" | "DATABASE":
                ret_val = DatabaseLocationSchema.FromDict(name=f"{name}Location", unparsed_elements=_location)

        return ret_val

    # *** PRIVATE METHODS ***
    