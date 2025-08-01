## import standard libraries
import logging
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple, Optional, Self
## import local files
from ogd.common.models.Feature import Feature
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.tables.FeatureMapSchema import FeatureMapSchema
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

## @class TableSchema
class FeatureTableSchema(TableSchema):
    """Dumb struct to hold info about the structure of data for a particular game, from a particular source.
        In particular, it contains an ordered list of columns in the data source table,
        and a mapping of those columns to the corresponding elements of a formal OGD structure.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_COLUMNS = []

    def __init__(self, name,
                 column_map:Optional[FeatureMapSchema],
                 columns:Optional[List[ColumnSchema]],
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the TableSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "column_map": {
                "session_id"           : "session_id",
                "app_id"               : null,
                "timestamp"            : ["client_time", "client_time_ms"],
                ...
            },

            "columns": [
                {
                    "name": "session_id",
                    "readable": "Session ID",
                    "description": "ID for the play session",
                    "type": "str"
                },
                {
                    "name": "client_time",
                    ...
                },
        },
        ```

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        unparsed_elements : Map = other_elements or {}

        self._column_map : FeatureMapSchema = column_map or self._parseColumnMap(unparsed_elements=unparsed_elements)
        super().__init__(name=name, columns=columns, other_elements=unparsed_elements)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def ColumnMap(self) -> FeatureMapSchema:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indicies, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._column_map

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        _columns_markdown = "\n".join([item.AsMarkdown for item in self.Columns])
        ret_val = "\n\n".join([
            "## Database Columns",
            "The individual columns recorded in the database for this game.",
            _columns_markdown,
            "## Feature Object Elements",
            "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.",
            self.ColumnMap.AsMarkdown,
            ""]
        )
        return ret_val

    @classmethod
    def Default(cls) -> "FeatureTableSchema":
        return FeatureTableSchema(
            name="DefaultFeatureTableSchema",
            column_map=FeatureMapSchema.Default(),
            columns=cls._DEFAULT_COLUMNS,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "FeatureTableSchema":
        """Function to generate a TableSchema from a dictionary.

        The structure is assumed to be as follows:
        ```python
        {
            "table_type" : <either EVENT or FEATURE>,
            "columns" : [<list of column schemas>],
            "column_map" : {<mapping of column names to indices>}
        }
        ```

        The specific handling of the column map will be determined by the specific TableSchema subclass on which the FromDict feature is called.

        :param name: The name of the returned TableSchema object
        :type name: str
        :param all_elements: A dictionary containing all elements to be parsed into the TableSchema object
        :type all_elements: Dict[str, Any]
        :param logger: An optional logger for outputting errors/warnings, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: An instance of the TableSchema subclass on which the function is called
        :rtype: TableSchema
        """
        return FeatureTableSchema(name=name, column_map=None, columns=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    _conversion_warnings = Counter()
    def FeatureFromRow(self, row:Tuple, concatenator:str = '.', fallbacks:Map={}) -> Feature:
        """Function to convert a row to a Feature, based on the loaded schema.
        In general, columns specified in the schema's column_map are mapped to corresponding elements of the Event.
        If the column_map gave a list, rather than a single column name, the values from each column are concatenated in order with '.' character separators.
        Finally, the concatenated values (or single value) are parsed according to the type required by Event.
        One exception: For event_data, we expect to create a Dict object, so each column in the list will have its value parsed according to the type in 'columns',
            and placed into a dict mapping the original column name to the parsed value (unless the parsed value is a dict, then it is merged into the top-level dict).

        .. TODO Use conversions utils to deal with the types we're getting from the row.

        :param row: _description_
        :type row: Tuple
        :param concatenator: _description_, defaults to '.'
        :type concatenator: str, optional
        :param fallbacks: _description_, defaults to {}
        :type fallbacks: Map, optional
        :raises TypeError: _description_
        :return: _description_
        :rtype: Event
        """
        if not isinstance(self.ColumnMap, FeatureMapSchema):
            raise TypeError(f"{self.Name} contains a mapping for Features, not Events!")

        # define vars to be passed as params
        feat_name  : str
        feat_type  : str
        game_unit  : str
        unit_index : int
        app_id     : str
        user_id    : Optional[str]
        sess_id    : str
        subfeats   : List[str] 
        values     : List[Any]
        

        # 1. Get Feature info
        idx = self._indexFromMapping(self.ColumnMap.FeatureNameColumn)
        feat_name = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=None)
        if not isinstance(feat_name, str):
            if "feat_name" not in self._conversion_warnings:
                _msg = f"{self.Name} feature table schema set feat_name as {type(feat_name)}, but feat_name should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["feat_name"] += 1
            feat_name = str(feat_name)

        idx = self._indexFromMapping(self.ColumnMap.FeatureTypeColumn)
        feat_type = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=None)
        if not isinstance(feat_type, str):
            if "feat_type" not in self._conversion_warnings:
                _msg = f"{self.Name} feature table schema set feat_type as {type(feat_type)}, but feat_type should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["feat_type"] += 1
            feat_type = str(feat_type)

        # 2. Get game unit info
        idx = self._indexFromMapping(self.ColumnMap.GameUnitColumn)
        game_unit = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=None)
        if not isinstance(game_unit, str):
            if "game_unit" not in self._conversion_warnings:
                _msg = f"{self.Name} feature table schema set game_unit as {type(game_unit)}, but game_unit should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["game_unit"] += 1
            game_unit = str(game_unit)

        idx = self._indexFromMapping(self.ColumnMap.GameUnitIndexColumn)
        unit_index = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=None)
        if not isinstance(unit_index, int):
            if "unit_index" not in self._conversion_warnings:
                _msg = f"{self.Name} feature table schema set unit_index as {type(unit_index)}, but unit_index should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["unit_index"] += 1
            unit_index = str(unit_index)

        # 3. Get ID data
        idx = self._indexFromMapping(self.ColumnMap.AppIDColumn)
        app_id = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=None)
        if not isinstance(app_id, str):
            if "app_id" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set app_id as {type(app_id)}, but app_id should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["app_id"] += 1
            app_id = str(app_id)

        idx = self._indexFromMapping(self.ColumnMap.UserIDColumn)
        user_id = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=None)
        if user_id is not None and not isinstance(user_id, str):
            if "uid" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set user_id as {type(user_id)}, but user_id should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["uid"] += 1
            user_id = str(user_id)

        idx = self._indexFromMapping(self.ColumnMap.SessionIDColumn)
        sess_id = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=None)
        if not isinstance(sess_id, str):
            if "sess_id" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set session_id as {type(sess_id)}, but session_id should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["sess_id"] += 1
            sess_id = str(sess_id)

        # 4. Get feature-specific data
        idx = self._indexFromMapping(self.ColumnMap.SubfeaturesColumn)
        subfeats = self._valueFromRow(row=row, indices=idx,   concatenator=concatenator, fallback=None)

        idx = self._indexFromMapping(self.ColumnMap.ValuesColumn)
        values = self._valueFromRow(row=row, indices=idx,   concatenator=concatenator, fallback=None)

        return Feature(name=feat_name, feature_type=feat_type,
                       game_unit=game_unit, game_unit_index=unit_index,
                       app_id=app_id, user_id=user_id, session_id=sess_id,
                       subfeatures=subfeats, values=values)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    @staticmethod
    def _parseColumnMap(unparsed_elements:Map) -> FeatureMapSchema:
        ret_val : FeatureMapSchema

        raw_map = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["column_map"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if raw_map:
            ret_val = FeatureMapSchema.FromDict(name="ColumnMap", unparsed_elements=raw_map)
        else:
            ret_val = FeatureMapSchema.Default()

        return ret_val
