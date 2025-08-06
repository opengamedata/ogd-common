# import libraries
import logging
from datetime import datetime
from itertools import chain
from typing import Dict, List, LiteralString, Optional, Tuple
# 3rd-party imports
from mysql.connector import connection, cursor
# import locals
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.MySQLConnector import MySQLConnector
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.storage.MySQLConfig import MySQLConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Pair

class MySQLInterface(Interface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, fail_fast:bool, store:Optional[MySQLConnector]=None):
        super().__init__(config=config, fail_fast=fail_fast)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, MySQLConfig):
            self._store = MySQLConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"MySQLInterface config was for a connector other than MySQL! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> MySQLConnector:
        return self._store

    def _availableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> List[str]:
        if self.Connector.Cursor is not None and isinstance(self.Config.StoreConfig, MySQLConfig):
            id_col : LiteralString       = "session_id" if mode==IDMode.SESSION else "user_id"
            # 1. If we're in shared table, then need to filter on game ID
            where_clause, params = self._generateWhereClause(filters=filters)
            if self.Config.TableName != self.Config.GameID:
                where_clause += "\nAND `app_id`=%s"
                params.append(self.Config.GameID)
            query = f"""
                SELECT DISTINCT(`{id_col}`)
                FROM `{self.Config.TableLocation.Location}`
                {where_clause}
            """
            data = MySQLInterface.Query(cursor=self.Connector.Cursor, query=query, params=tuple(params))
            return [str(id[0]) for id in data] if data != None else []
        else:
            Logger.Log(f"Could not get list of all session ids, MySQL connection is not open.", logging.WARN)
            return []

    # def _IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]]=None) -> List[str]:
    #     ret_val = []
    #     if self._db_cursor is not None and isinstance(self.GameStoreConfig.Source, MySQLConfig):
    #         # alias long setting names.
    #         _db_name     : str = self.GameStoreConfig.DatabaseName
    #         _table_name  : str = self.GameStoreConfig.TableName

    #         # prep filter strings
    #         filters = []
    #         params = []
    #         if _table_name != self._game_id:
    #             filters.append(f"`app_id`=%s")
    #             params.append(self._game_id)
    #         # if versions is not None and versions is not []:
    #         #     filters.append(f"app_version in ({','.join([str(version) for version in versions])})")
    #         filters.append(f"`{self._TableConfig.EventSequenceIndexColumn}`='0'")
    #         filters.append(f"(`server_time` BETWEEN '{min.isoformat()}' AND '{max.isoformat()}')")
    #         filter_clause = " AND ".join(filters)

    #         # run query
    #         # We grab the ids for all sessions that have 0th move in the proper date range.
    #         sess_id_col = self._TableConfig.SessionIDColumn or "`session_id`"
    #         sess_ids_raw = SQL.SELECT(cursor=self._db_cursor,   db_name=_db_name,     table=_table_name,
    #                                  columns=[sess_id_col],     filter=filter_clause,
    #                                  sort_columns=[sess_id_col], sort_direction="ASC", distinct=True,
    #                                  params=tuple(params))
    #         if sess_ids_raw is not None:
    #             ret_val = [str(sess[0]) for sess in sess_ids_raw]
    #     else:
    #         Logger.Log(f"Could not get session list for {min.isoformat()}-{max.isoformat()} range, MySQL connection is not open or config was not for MySQL.", logging.WARN)
    #     return ret_val

    def _availableDates(self, id_filter:IDFilterCollection, version_filter:VersioningFilterCollection) -> Dict[str,datetime]:
        ret_val = {'min':datetime.now(), 'max':datetime.now()}
        if self._db_cursor is not None and isinstance(self.GameStoreConfig.Source, MySQLConfig):
            _db_name     : str = self.GameStoreConfig.DatabaseName
            _table_name  : str = self.GameStoreConfig.TableName

            # prep filter strings
            filters = []
            params  = []
            if _table_name != self.GameStoreConfig.GameID:
                filters.append(f"`app_id`=%s")
                params.append(self.GameStoreConfig.GameID)
            filter_clause = " AND ".join(filters)

            # run query
            result = SQL.SELECT(cursor=self._db_cursor, db_name=_db_name, table=_table_name,
                                columns=['MIN(server_time)', 'MAX(server_time)'], filter=filter_clause,
                                params =tuple(params))
            if result is not None:
                ret_val = {'min':result[0][0], 'max':result[0][1]}
        else:
            Logger.Log(f"Could not get full date range, MySQL connection is not open or config was not for MySQL.", logging.WARN)
        return ret_val

    # def _datesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> Dict[str, datetime]:
    #     ret_val = {'min':datetime.now(), 'max':datetime.now()}
    #     if self._db_cursor is not None and isinstance(self.GameStoreConfig.Source, MySQLConfig):
    #         # alias long setting names.
    #         _db_name     : str = self.GameStoreConfig.DatabaseName
    #         _table_name  : str = self.GameStoreConfig.TableName
            
    #         # prep filter strings
    #         filters = []
    #         params = tuple()
    #         if _table_name != self._game_id:
    #             filters.append(f"`app_id`=%s")
    #             params = tuple(self._game_id)
    #         # if versions is not None and versions is not []:
    #         #     filters.append(f"app_version in ({','.join([str(version) for version in versions])})")
    #         ids_string = ','.join([f"'{x}'" for x in id_list])
    #         if id_mode == IDMode.SESSION:
    #             sess_id_col = self._TableConfig.SessionIDColumn or "session_id"
    #             filters.append(f"{sess_id_col} IN ({ids_string})")
    #         elif id_mode == IDMode.USER:
    #             play_id_col = self._TableConfig.UserIDColumn or "player_id"
    #             filters.append(f"`{play_id_col}` IN ({ids_string})")
    #         else:
    #             raise ValueError("Invalid IDMode in MySQLInterface!")
    #         filter_clause = " AND ".join(filters)
    #         # run query
    #         result = SQL.SELECT(cursor=self._db_cursor,      db_name=_db_name,    table=_table_name,
    #                             columns=['MIN(server_time)', 'MAX(server_time)'], filter=filter_clause,
    #                             params=params)
    #         if result is not None:
    #             ret_val = {'min':result[0][0], 'max':result[0][1]}
    #     else:
    #         Logger.Log(f"Could not get date range for {len(id_list)} sessions, MySQL connection is not open.", logging.WARN)
    #     return ret_val

    def _availableVersions(self, mode:VersionType, id_filter:IDFilterCollection, date_filter:SequencingFilterCollection) -> List[SemanticVersion | str]:
        return []

    def _getEventRows(self, id_filter:IDFilterCollection, date_filter:SequencingFilterCollection, version_filter:VersioningFilterCollection, event_filter:EventFilterCollection) -> List[Tuple]:
        ret_val = []
        # grab data for the given session range. Sort by event time, so
        if self._db_cursor is not None and isinstance(self.GameStoreConfig.Source, MySQLConfig):
            # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
            _db_name     : str = self.GameStoreConfig.DatabaseName
            _table_name  : str = self.GameStoreConfig.TableName

            sess_id_col = self.GameStoreConfig.SchemaName.SessionIDColumn or 'session_id'
            play_id_col = self.GameStoreConfig.SchemaName.UserIDColumn or 'player_id'
            seq_idx_col = self.GameStoreConfig.SchemaName.EventSequenceIndexColumn or 'session_n'
            evt_nam_col = self.GameStoreConfig.SchemaName.EventNameColumn or "event_name"

            filters = []
            params = []
            if _table_name != self.GameStoreConfig.GameID:
                filters.append(f"`app_id`=%s")
                params.append(self.GameStoreConfig.GameID)
            # if versions is not None and versions is not []:
            #     filters.append(f"app_version in ({','.join([str(version) for version in versions])})")
            id_param_string = ",".join( [f"%s"]*len(id_list) )
            if id_mode == IDMode.SESSION:
                filters.append(f"`{sess_id_col}` IN ({id_param_string})")
                params += [str(id) for id in id_list]
            elif id_mode == IDMode.USER:
                filters.append(f"`{play_id_col}` IN ({id_param_string})")
                params += [str(id) for id in id_list]
            else:
                raise ValueError("Invalid IDMode in MySQLInterface!")
            if exclude_rows is not None:
                evt_name_param_string = ",".join( ["%s"]*len(exclude_rows) )
                filters.append(f"`{evt_nam_col}` not in ({evt_name_param_string})")
                params += [str(name) for name in exclude_rows]
            filter_clause = " AND ".join(filters)

            data = SQL.SELECT(cursor=self._db_cursor, db_name=_db_name,                        table=_table_name,
                              filter=filter_clause,   sort_columns=[sess_id_col, seq_idx_col], sort_direction="ASC",
                              params=tuple(params))
            if data is not None:
                ret_val = data
            # self._select_queries.append(select_query) # this doesn't appear to be used???
        else:
            Logger.Log(f"Could not get data for {len(id_list)} sessions, MySQL connection is not open or config was not for MySQL.", logging.WARN)
        return ret_val

    # *** PUBLIC STATICS ***

    # Function to build and execute SELECT statements on a database connection.
    # @staticmethod
    # def SELECT(cursor        : cursor.MySQLCursor,
    #            db_name       : str,                                  table          : str,
    #            columns       : List[LiteralString]           = [],   where_clause   : LiteralString = "",
    #            sort_columns  : Optional[List[LiteralString]] = None, sort_direction : LiteralString = "ASC",
    #            grouping      : Optional[LiteralString]       = None, distinct       : bool          = False, 
    #            offset        : int                           = 0,    limit          : int           = -1,
    #            fetch_results : bool                          = True, params         : Tuple         = tuple()) -> Optional[List[Tuple]]:
    #     """Function to build and execute SELECT statements on a database connection.

    #     :param cursor: A database cursor, retrieved from the active connection.
    #     :type cursor: cursor.MySQLCursor
    #     :param db_name: The name of the database to which we are connected.
    #     :type db_name: str
    #     :param table: The name of the table from which we want to make a selection.
    #     :type table: str
    #     :param columns: A list of columns to be selected. If empty (or None), all columns will be used (SELECT * FROM ...). Defaults to None
    #     :type columns: List[str], optional
    #     :param filter: A string giving the constraints for a WHERE clause (The "WHERE" term itself should not be part of the filter string), defaults to None
    #     :type filter: str, optional
    #     :param sort_columns: A list of columns to sort results on. The order of columns in the list is the order given to SQL. Defaults to None
    #     :type sort_columns: List[str], optional
    #     :param sort_direction: The "direction" of sorting, either ascending or descending., defaults to "ASC"
    #     :type sort_direction: str, optional
    #     :param grouping: A column name to group results on. Subject to SQL rules for grouping, defaults to None
    #     :type grouping: str, optional
    #     :param distinct: A bool to determine whether to select only rows with distinct values in the column, defaults to False
    #     :type distinct: bool, optional
    #     :param limit: The maximum number of rows to be selected. Use -1 for no limit., defaults to -1
    #     :type limit: int, optional
    #     :param fetch_results: A bool to determine whether all results should be fetched and returned, defaults to True
    #     :type fetch_results: bool, optional
    #     :return: A collection of all rows from the selection, if fetch_results is true, otherwise None.
    #     :rtype: Optional[List[Tuple]]
    #     """
    #     d          = "DISTINCT" if distinct else ""
    #     cols       = ",".join([f"{col}" for col in columns]) if len(columns) > 0 else "*"
    #     sort_cols  = ",".join([f"`{col}`" for col in sort_columns]) if sort_columns is not None and len(sort_columns) > 0 else None
    #     table_path = db_name + "." + str(table)

    #     sel_clause = f"SELECT {d} {cols} FROM {table_path}"
    #     group_clause = "" if grouping  is None else f"GROUP BY {grouping}"
    #     sort_clause  = "" if sort_cols is None else f"ORDER BY {sort_cols} {sort_direction}"
    #     lim_clause   = "" if limit < 0         else f"LIMIT {str(max(offset, 0))}, {str(limit)}" # don't use a negative for offset
    #     query = f"{sel_clause} {where_clause} {group_clause} {sort_clause} {lim_clause};"
    #     return SQL.Query(cursor=cursor, query=query, params=params, fetch_results=fetch_results)

    @staticmethod
    def Query(cursor:cursor.MySQLCursor, query:str, params:Optional[Tuple], fetch_results: bool = True) -> Optional[List[Tuple]]:
        ret_val : Optional[List[Tuple]] = None
        # first, we do the query.
        Logger.Log(f"Running query: {query}\nWith params: {params}", logging.DEBUG, depth=3)
        start = datetime.now()
        cursor.execute(query, params)
        time_delta = datetime.now()-start
        Logger.Log(f"Query execution completed, time to execute: {time_delta}", logging.DEBUG)
        # second, we get the results.
        if fetch_results:
            ret_val = cursor.fetchall()
            time_delta = datetime.now()-start
            Logger.Log(f"Query fetch completed, total query time:    {time_delta} to get {len(ret_val) if ret_val is not None else 0:d} rows", logging.DEBUG)
        return ret_val

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _generateWhereClause(filters:DatasetFilterCollection) -> Pair[str, List[str | int]]:
        exclude : LiteralString

        sess_clause : Optional[LiteralString] = None
        sess_param  : List[str] = []
        if filters.IDFilters.Sessions.Active:
            sess_param = filters.IDFilters.Sessions.AsList or []
            if len(sess_param) > 0:
                exclude = "NOT" if filters.IDFilters.Sessions.FilterMode == FilterMode.EXCLUDE else ""
                id_param_string : LiteralString = ("%s, " * len(sess_param))[:-2] # take all but the trailing ', '.
                sess_clause = f"`session_id` {exclude} IN ({id_param_string})"

        users_clause : Optional[LiteralString] = None
        users_param  : List[str] = []
        if filters.IDFilters.Players.Active:
            users_param = filters.IDFilters.Players.AsList or []
            if len(users_param) > 0:
                exclude = "NOT" if filters.IDFilters.Players.FilterMode == FilterMode.EXCLUDE else ""
                id_param_string : LiteralString = ("%s, " * len(users_param))[:-2] # take all but the trailing ', '.
                users_clause = f"`user_id` {exclude} IN ({id_param_string})"

        times_clause : Optional[LiteralString] = None
        times_param  : List[str] = []
        if filters.Sequences.Timestamps.Active:
            if filters.Sequences.Timestamps.Min and filters.Sequences.Timestamps.Max:
                exclude = "NOT" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ""
                times_clause = f"`client_time` {exclude} BETWEEN %s and %s"
                times_param = [filters.Sequences.Timestamps.Min.isoformat(), filters.Sequences.Timestamps.Max.isoformat()]
            elif filters.Sequences.Timestamps.Min:
                exclude = "<" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                times_clause = f"`client_time` {exclude} %s"
                times_param = [filters.Sequences.Timestamps.Min.isoformat()]
            elif filters.Sequences.Timestamps.Max:
                exclude = ">" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                times_clause = f"`client_time` {exclude} %s"
                times_param = [filters.Sequences.Timestamps.Max.isoformat()]

        indices_clause : Optional[LiteralString] = None
        indices_param  : List[int] = []
        if filters.Sequences.SessionIndices.Active:
            indices_param = filters.Sequences.SessionIndices.AsList or []
            if len(indices_param) > 0:
                exclude = "NOT" if filters.Sequences.SessionIndices.FilterMode == FilterMode.EXCLUDE else ""
                indices_param_string : LiteralString = ("%s, " * len(indices_param))[:-2] # take all but the trailing ', '.
                indices_clause = f"`event_session_index` {exclude} IN ({indices_param_string})"

        log_clause : Optional[LiteralString] = None
        log_param  : List[str] =  []
        if filters.Versions.LogVersions.Active:
            if isinstance(filters.Versions.LogVersions, SetFilter):
                log_param = [str(ver) for ver in filters.Versions.LogVersions.AsList] if filters.Versions.LogVersions.AsList else []
                if len(log_param) > 0:
                    exclude = "NOT" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                    log_param_string : LiteralString = ("%s, " * len(log_param))[:-2] # take all but the trailing ', '.
                    log_clause = f"`log_version` {exclude} IN ({log_param_string})"
            elif isinstance(filters.Versions.LogVersions, RangeFilter):
                if filters.Versions.LogVersions.Min and filters.Versions.LogVersions.Max:
                    exclude = "NOT" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                    log_clause = f"`log_version` {exclude} BETWEEN %s AND %s"
                    log_param = [str(filters.Versions.LogVersions.Min), str(filters.Versions.LogVersions.Max)]
                elif filters.Versions.LogVersions.Min:
                    exclude = "<" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    log_clause = f"`log_version` {exclude} %s"
                    log_param = [str(filters.Versions.LogVersions.Min)]
                else: # version_filter.LogVersionFilter.Max is not None
                    exclude = ">" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    log_clause = f"`log_version` {exclude} %s"
                    log_param = [str(filters.Versions.LogVersions.Max)]

        app_clause : Optional[LiteralString] = None
        app_param  : List[str] = []
        if filters.Versions.AppVersions.Active:
            if isinstance(filters.Versions.AppVersions, SetFilter):
                app_param = [str(ver) for ver in filters.Versions.AppVersions.AsList] if filters.Versions.AppVersions.AsList else []
                if len(app_param) > 0:
                    exclude = "NOT" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                    app_param_string : LiteralString = ("%s, " * len(app_param))[:-2] # take all but the trailing ', '.
                    app_clause = f"`app_version` {exclude} IN ({app_param_string})"
            elif isinstance(filters.Versions.AppVersions, RangeFilter):
                if filters.Versions.AppVersions.Min and filters.Versions.AppVersions.Max:
                    exclude = "NOT" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                    app_clause = f"`app_version` {exclude} BETWEEN %s and %s"
                    app_param = [str(filters.Versions.AppVersions.Min), str(filters.Versions.AppVersions.Max)]
                elif filters.Versions.AppVersions.Min:
                    exclude = "<" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    app_clause = f"`app_version` {exclude} %s"
                    app_param = [str(filters.Versions.AppVersions.Min)]
                else: # version_filter.AppVersionFilter.Max is not None
                    exclude = ">" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    app_clause = f"`app_version` {exclude} %s"
                    app_param = [str(filters.Versions.AppVersions.Max)]

        branch_clause : Optional[LiteralString] = None
        branch_param  : List[str] = []
        if filters.Versions.AppBranches.Active:
            if isinstance(filters.Versions.AppBranches, SetFilter):
                branch_param = [str(ver) for ver in filters.Versions.AppBranches.AsList] if filters.Versions.AppBranches.AsList else []
                if len(branch_param) > 0:
                    exclude = "NOT" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                    branch_param_string : LiteralString = ("%s, " * len(branch_param))[:-2] # take all but the trailing ', '.
                    branch_clause = f"`app_branch` {exclude} IN ({branch_param_string})"
            elif isinstance(filters.Versions.AppBranches, RangeFilter):
                if filters.Versions.AppBranches.Min and filters.Versions.AppBranches.Max:
                    exclude = "NOT" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                    branch_clause = f"`app_branch` {exclude} BETWEEN %s and %s"
                    app_param = [str(filters.Versions.AppBranches.Min), str(filters.Versions.AppBranches.Max)]
                elif filters.Versions.AppBranches.Min:
                    exclude = "<" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    branch_clause = f"`app_branch` {exclude} %s"
                    app_param = [str(filters.Versions.AppBranches.Min)]
                else: # version_filter.AppBranchFilter.Max is not None
                    exclude = ">" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    branch_clause = f"`app_branch` {exclude} %s"
                    app_param = [str(filters.Versions.AppBranches.Max)]

        events_clause : Optional[LiteralString] = None
        events_param  : List[str] = []
        if filters.Events.EventNames.Active:
            events_param = filters.Events.EventNames.AsList or []
            if len(events_param) > 0:
                exclude = "NOT" if filters.Events.EventNames.FilterMode == FilterMode.EXCLUDE else ""
                events_param_string : LiteralString = ("%s, " * len(events_param))[:-2] # take all but the trailing ', '.
                events_clause = f"`event_name` {exclude} IN ({events_param_string})"

        # codes_clause : Optional[LiteralString] = None
        # codes_param  : List[BigQueryParameter] = []
        # if event_filter.EventCodeFilter:
        #     if isinstance(filters.Events.EventCodeFilter, SetFilter) and len(event_filter.EventCodeFilter.AsSet) > 0:
        #         exclude = "NOT" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ""
        #         codes_clause = f"`event_code` {exclude} IN @app_branchs"
        #         codes_param.append(
        #             bigquery.ArrayQueryParameter(name="app_branchs", array_type="INT64", values=filters.Events.EventCodeFilter.AsList)
        #         )
        #     elif isinstance(event_filter.EventCodeFilter, RangeFilter):
        #         if filters.Events.EventCodeFilter.Min and event_filter.EventCodeFilter.Max:
        #             exclude = "NOT" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ""
        #             codes_clause = f"`event_code` {exclude} BETWEEN @event_codes_range"
        #             codes_param.append(
        #                 bigquery.RangeQueryParameter(name="event_codes_range", range_element_type="INT64", start=filters.Events.EventCodeFilter.Min, end=event_filter.EventCodeFilter.Max)
        #             )
        #         elif filters.Events.EventCodeFilter.Min:
        #             exclude = "<" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
        #             codes_clause = f"`event_code` {exclude} @event_codes_min"
        #             codes_param.append(
        #                 bigquery.ScalarQueryParameter(name="event_codes_min", type_="STRING", value=str(filters.Events.EventCodeFilter.Min))
        #             )
        #         else: # filters.Events.EventCodeFilter.Max is not None
        #             exclude = ">" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
        #             codes_clause = f"`event_code` {exclude} @event_codes_max"
        #             codes_param.append(
        #                 bigquery.ScalarQueryParameter(name="event_codes_max", type_="STRING", value=str(filters.Events.EventCodeFilter.Max))
        #             )

        # clause_list_raw : List[Optional[LiteralString]] = [sess_clause, users_clause, times_clause, indices_clause, log_clause, app_clause, branch_clause, events_clause, codes_clause]
        clause_list_raw : List[Optional[LiteralString]] = [sess_clause, users_clause, times_clause, indices_clause, log_clause, app_clause, branch_clause, events_clause]
        clause_list     : List[LiteralString]           = [clause for clause in clause_list_raw if clause is not None]
        where_clause    : LiteralString                 = f"WHERE {'\nAND '.join(clause_list)}" if len(clause_list) > 0 else ""

        # params_collection = [sess_param, users_param, times_param, indices_param, log_param, app_param, branch_param, events_param, codes_param]
        params_collection = [sess_param, users_param, times_param, indices_param, log_param, app_param, branch_param, events_param]
        params = list(chain.from_iterable(params_collection))

        return (where_clause, params)


    # *** PRIVATE METHODS ***
