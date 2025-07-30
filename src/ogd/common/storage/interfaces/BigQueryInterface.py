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
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

class BigQueryInterface(Interface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, fail_fast:bool, store:Optional[BigQueryConnector]):
        self._store : BigQueryConnector

        super().__init__(config=config, fail_fast=fail_fast)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, BigQueryConfig):
            self._store = BigQueryConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"BigQueryInterface config was for a connector other than BigQuery! Found config type {type(self.Config.StoreConfig)}")
        self._store.Open()

    @property
    def DBPath(self) -> str:
        """The path of form "[projectID].[datasetID].[tableName]" used to make queries

        TODO : do something more... clever than directly using configured values. That's how it's been so far, and that's fine,
        but wouldn't want any clever inputs here.

        :return: The full path from project ID to table name, if properly set in configuration, else the literal string "INVALID SOURCE SCHEMA".
        :rtype: str
        """
        return f"{self.Connector.StoreConfig.Location.DatabaseName}.{self.Config.TableLocation.Location}_*"


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> BigQueryConnector:
        return self._store

    def _availableIDs(self, mode:IDMode, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection) -> List[str]:
        ret_val = []

        if self.Connector.Client:
            id_col = "session_id" if mode==IDMode.SESSION else "user_id"
            suffix = self._generateSuffixClause(date_filter=date_filter)
            where_clause = f"WHERE {suffix}" if suffix else ""
            query = f"""
                SELECT DISTINCT {id_col}
                FROM `{self.DBPath}`
                {where_clause}
            """
            Logger.Log(f"Running query for all ids:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query)
            except BadRequest as err:
                Logger.Log(f"In _availableIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row[id_col]) for row in data]
                Logger.Log(f"Found {len(ret_val)} ids. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    def _availableDates(self, id_filter:IDFilterCollection, version_filter:VersioningFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str, datetime] = {}

        if self.Connector.Client:
            sess_clause = None
            users_clause = None
            if id_filter.SessionFilter:
                sess_string = ','.join([f"'{x}'" for x in id_filter.SessionFilter.AsSet])
                sess_clause = f"session_id IN ({sess_string})"
            if id_filter.PlayerFilter:
                users_string = ','.join([f"'{x}'" for x in id_filter.PlayerFilter.AsSet])
                users_clause = f"session_id IN ({users_string})"
            clause_collection = [clause for clause in [sess_clause, users_clause] if clause is not None]
            where_clause = f"WHERE {' AND '.join(clause_collection)}" if len(clause_collection) > 0 else ""

            query = f"""
                SELECT MIN(server_time), MAX(server_time)
                FROM `{self.DBPath}`
                {where_clause}
            """
            Logger.Log(f"Running query for full date range:\n{query}", logging.DEBUG, depth=3)

            try:
                data = list(self.Connector.Client.query(query))
                Logger.Log(f"...Query yielded results:\n{data}", logging.DEBUG, depth=3)
            except BadRequest as err:
                Logger.Log(f"In _availableDates, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                if len(data) == 1:
                    dates = data[0]
                    if len(dates) == 2 and dates[0] is not None and dates[1] is not None:
                        _min = dates[0] if type(dates[0]) == datetime else datetime.strptime(str(dates[0]), "%m-%d-%Y %H:%M:%S")
                        _max = dates[1] if type(dates[1]) == datetime else datetime.strptime(str(dates[1]), "%m-%d-%Y %H:%M:%S")
                        ret_val = {'min':_min, 'max':_max}
                    else:
                        Logger.Log("BigQueryInterface query did not give both a min and a max, setting both to 'now'", logging.WARNING, depth=3)
                        ret_val = {'min':datetime.now(), 'max':datetime.now()}
                else:
                    Logger.Log("BigQueryInterface query did not return any results, setting both min and max to 'now'", logging.WARNING, depth=3)
                    ret_val = {'min':datetime.now(), 'max':datetime.now()}
        else:
            Logger.Log(f"Can't retrieve available dates from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
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

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    @staticmethod
    def _generateSuffixClause(date_filter:TimingFilterCollection) -> Optional[str]:
        ret_val = None
        
        if date_filter.TimestampFilter and date_filter.TimestampFilter.Min and date_filter.TimestampFilter.Max:
            str_min, str_max = date_filter.TimestampFilter.Min.strftime("%Y%m%d"), date_filter.TimestampFilter.Max.strftime("%Y%m%d")
            ret_val = f"_TABLE_SUFFIX BETWEEN '{str_min}' AND '{str_max}'"
        
        return ret_val

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
