import json
import logging
from datetime import datetime, date
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
from typing import Dict, Final, List, Tuple, Optional
# import locals
from ogd.common.filters.collections import *
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

class BigQueryInterface(Interface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, store:BigQueryConnector, config:GameStoreConfig, fail_fast:bool):
        super().__init__(config=config, fail_fast=fail_fast)
        self._store = store
        self._store.Open()

    @property
    def FormattedSessionIDColumn(self) -> str:
        ret_val : str = "session_id"

        if self.Config.Table is not None:
            col_elem = self.Config.Table.ColumnMap.SessionIDColumn
            if isinstance(col_elem, str):
                ret_val = col_elem
            elif isinstance(col_elem, list):
                _concat = ", '.', ".join([f"`{col}`" for col in col_elem])
                ret_val = (f"concat({_concat}) as session_id")

        return ret_val

    @property
    def FormattedUserIDColumn(self) -> str:
        ret_val : str = "session_id"

        if self.Config.Table is not None:
            col_elem = self.Config.Table.ColumnMap.UserIDColumn
            if isinstance(col_elem, str):
                ret_val = col_elem
            elif isinstance(col_elem, list):
                _concat = ", '.', ".join([f"`{col}`" for col in col_elem])
                ret_val = (f"concat({_concat}) as user_id")

        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> BigQueryConnector:
        return self._store

    def _availableIDs(self, mode:IDMode, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection) -> List[str]:
        ret_val = []

        _id_clause = self.FormattedSessionIDColumn if mode == IDMode.SESSION else self.FormattedUserIDColumn
        query = f"""
            SELECT DISTINCT {_id_clause}
            FROM `{self.DBPath()}`,
        """
        Logger.Log(f"Running query for all ids:\n{query}", logging.DEBUG, depth=3)
        try:
            data = self.Connector.Client.query(query)
            session_ids = [str(row['session_id']) for row in data]
        except BadRequest as err:
            Logger.Log(f"In _allIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
        else:
            ret_val = session_ids
        return ret_val

    def _fullDateRange(self) -> Dict[str, datetime]:
        ret_val : Dict[str, datetime] = {}

        query = f"""
            SELECT MIN(server_time), MAX(server_time)
            FROM `{self.DBPath()}`
        """
        Logger.Log(f"Running query for full date range:\n{query}", logging.DEBUG, depth=3)
        try:
            data = list(self._client.query(query))
            date_range : Dict[str, datetime] = { 'min':data[0][0], 'max':data[0][1] }
        except BadRequest as err:
            Logger.Log(f"In _fullDateRange, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
        else:
            ret_val = date_range
        return ret_val

    def _rowsFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]] = None, exclude_rows:Optional[List[str]]=None) -> List[Tuple]:
        # 2) Set up clauses to select based on Session ID or Player ID.
        ret_val = []
        if self._client != None:
            query = self._generateRowFromIDQuery(id_list=id_list, id_mode=id_mode, exclude_rows=exclude_rows)
            Logger.Log(f"Running query for rows from IDs:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self._client.query(query)
                Logger.Log(f"...Query yielded results, with query in state: {data.state}", logging.DEBUG, depth=3)
            except BadRequest as err:
                Logger.Log(f"In _rowsFromIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                for row in data:
                    items = tuple(row.items())
                    event = []
                    for item in items:
                        match item[0]:
                            case "event_params":
                                _params = {param['key']:param['value'] for param in item[1]}
                                event.append(json.dumps(_params, sort_keys=True))
                            case "device":
                                event.append(json.dumps(item[1], sort_keys=True))
                            case _:
                                event.append(item[1])
                    ret_val.append(tuple(event))
        return ret_val

    def _IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]] = None) -> List[str]:
        ret_val = []
        str_min, str_max = min.strftime("%Y%m%d"), max.strftime("%Y%m%d")
        query = f"""
            SELECT DISTINCT session_id
            FROM `{self.DBPath(min_date=min.date(), max_date=max.date())}`
            WHERE _TABLE_SUFFIX BETWEEN '{str_min}' AND '{str_max}'
        """
        Logger.Log(f"Running query for ids from dates:\n{query}", logging.DEBUG, depth=3)
        try:
            data = self._client.query(query)
            ids = [str(row['session_id']) for row in data]
        except BadRequest as err:
            Logger.Log(f"In _IDsFromDates, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
        else:
            ret_val = ids
            Logger.Log(f"Found {len(ret_val)} ids. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        return ret_val

    def _datesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]] = None) -> Dict[str, datetime]:
        ret_val : Dict[str, datetime] = {}

        match id_mode:
            case IDMode.SESSION:
                id_string = ','.join([f"'{x}'" for x in id_list])
                where_clause = f"WHERE session_id IN ({id_string})"
            case IDMode.USER:
                id_string = ','.join([f"'{x}'" for x in id_list])
                where_clause = f"WHERE user_id IN ({id_string})"
            case _:
                Logger.Log(f"Invalid ID mode given (name={id_mode.name}, val={id_mode.value}), defaulting to session mode.", logging.WARNING, depth=3)
                id_string = ','.join([f"{x}" for x in id_list])
                where_clause = f"WHERE session_id IN ({id_string})"
        query = f"""
            SELECT MIN(server_time), MAX(server_time)
            FROM `{self.DBPath()}`
            {where_clause}
        """
        Logger.Log(f"Running query for dates from IDs:\n{query}", logging.DEBUG, depth=3)
        try:
            data = list(self._client.query(query))
            Logger.Log(f"...Query yielded results:\n{data}", logging.DEBUG, depth=3)
        except BadRequest as err:
            Logger.Log(f"In _datesFromIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}", logging.WARNING)
        else:
            if len(data) == 1:
                dates = data[0]
                if len(dates) == 2 and dates[0] is not None and dates[1] is not None:
                    _min = dates[0] if type(dates[0]) == datetime else datetime.strptime(str(dates[0]), "%m-%d-%Y %H:%M:%S")
                    _max = dates[1] if type(dates[1]) == datetime else datetime.strptime(str(dates[1]), "%m-%d-%Y %H:%M:%S")
                    ret_val = {'min':_min, 'max':_max}
                else:
                    Logger.Log(f"BigQueryInterface query did not give both a min and a max, setting both to 'now'", logging.WARNING, depth=3)
                    ret_val = {'min':datetime.now(), 'max':datetime.now()}
            else:
                Logger.Log(f"BigQueryInterface query did not return any results, setting both min and max to 'now'", logging.WARNING, depth=3)
                ret_val = {'min':datetime.now(), 'max':datetime.now()}
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def DBPath(self, filter:TimingFilterCollection) -> str:
        """The path of form "[projectID].[datasetID].[tableName]" used to make queries

        :return: The full path from project ID to table name, if properly set in configuration, else the literal string "INVALID SOURCE SCHEMA".
        :rtype: str
        """
        
        # _current_date = datetime.now().date()
        date_wildcard = "*"
        # if min_date is not None and max_date is not None:
        #     date_wildcard = BigQueryInterface._datesWildcard(a=min_date, b=max_date)
        # elif min_date is not None:
        #     date_wildcard = BigQueryInterface._datesWildcard(a=min_date, b=_current_date)
        # elif max_date is not None:
        #     date_wildcard = BigQueryInterface._datesWildcard(a=_current_date, b=max_date)
        return f"{self._config.Source.AsConnectionInfo}.{self._config.DatabaseName}.{self._config.TableName}_{date_wildcard}"

    # *** PRIVATE STATICS ***

    @staticmethod
    def _datesWildcard(a:date, b:date) -> str:
        ret_val = "*"
        if a.year == b.year:
            ret_val = str(a.year).rjust(4, "0")
            if a.month == b.month:
                ret_val += str(a.month).rjust(2, "0")
                if a.day == b.day:
                    ret_val += str(a.day).rjust(2, "0")
                else:
                    ret_val += "*"
            else:
                ret_val += "*"
        else:
            ret_val = "*"
        return ret_val

    # *** PRIVATE METHODS ***

    def _generateRowFromIDQuery(self, id_list:List[str], id_mode:IDMode, exclude_rows:Optional[List[str]]=None) -> str:
        id_clause : str = ""
        id_string = ','.join([f"'{x}'" for x in id_list])
        match id_mode:
            case IDMode.SESSION:
                id_clause = f"session_id IN ({id_string})"
            case IDMode.USER:
                id_clause  = f"user_id IN ({id_string})"
            case _:
                Logger.Log(f"Invalid ID mode given (name={id_mode.name}, val={id_mode.value}), defaulting to session mode.", logging.WARNING, depth=3)
                id_clause = f"session_id IN ({id_string})"
        # 3) Set up WHERE clause based on whether we need Aqualab min version or not.
        where_clause = f" WHERE {id_clause}"
        if exclude_rows is not None:
            exclude_string = ','.join([f"'{x}'" for x in exclude_rows])
            where_clause += f" AND event_name not in ({exclude_string})"

        # 4) Set up actual query
        # TODO Order by user_id, and by timestamp within that.
        # Note that this could prove to be wonky when we have more games without user ids,
        # will need to really rethink this when we start using new system.
        # Still, not a huge deal because most of these will be rewritten at that time anyway.
        query = f"""
            SELECT *
            FROM `{self.DBPath()}`
            {where_clause}
            ORDER BY `user_id`, `session_id`, `event_sequence_index` ASC
        """
        return query
