# standard imports
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from typing import Dict, Final, List, LiteralString, Optional, Tuple, Union
# 3rd-party imports
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
# OGD imports
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

type BigQueryParameter = Union[bigquery.ScalarQueryParameter, bigquery.ArrayQueryParameter, bigquery.RangeQueryParameter]
@dataclass
class ParamaterizedClause:
    clause: LiteralString
    params: List[BigQueryParameter]

class BigQueryInterface(Interface):
    """Implementation of Interface functions for BigQuery.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, fail_fast:bool, store:Optional[BigQueryConnector]=None):
        self._store : BigQueryConnector

        super().__init__(config=config, fail_fast=fail_fast)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, BigQueryConfig):
            self._store = BigQueryConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"BigQueryInterface config was for a connector other than BigQuery! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

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
            # 1. Create query & config
            id_col : LiteralString       = "session_id" if mode==IDMode.SESSION else "user_id"
            suffix : ParamaterizedClause = self._generateSuffixClause(date_filter=date_filter)
            suffix_clause = f"WHERE {suffix.clause}" if suffix.clause is not None else ""
            query = f"""
                SELECT DISTINCT {id_col}
                FROM `{self.DBPath}`
                {suffix_clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=suffix.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for all {mode} ids:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query, cfg)
            except BadRequest as err:
                Logger.Log(f"In _availableIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row[id_col]) for row in data]
                Logger.Log(f"Found {len(ret_val)} {mode} ids. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    def _availableDates(self, id_filter:IDFilterCollection, version_filter:VersioningFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str, datetime] = {}

        if self.Connector.Client:
            # 1. Create query & config
            where_clause = self._generateWhereClause(id_filter=id_filter, date_filter=TimingFilterCollection(None, None), version_filter=version_filter, event_filter=EventFilterCollection(None, None))
            query = f"""
                SELECT MIN(server_time), MAX(server_time)
                FROM `{self.DBPath}`
                {where_clause.clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for full date range:\n{query}", logging.DEBUG, depth=3)
            try:
                data = list(self.Connector.Client.query(query, job_config=cfg))
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

    def _availableVersions(self, mode:VersionType, id_filter:IDFilterCollection, date_filter:TimingFilterCollection) -> List[SemanticVersion | str]:
        ret_val : List[SemanticVersion | str] = []

        if self.Connector.Client:
            # 1. Create query & config
            version_col  : LiteralString       = "log_version" if mode==VersionType.LOG else "app_version" if mode==VersionType.APP else "app_branch"
            where_clause : ParamaterizedClause = self._generateWhereClause(id_filter=id_filter, date_filter=date_filter, version_filter=VersioningFilterCollection(None, None), event_filter=EventFilterCollection(None, None))
            query = f"""
                SELECT DISTINCT {version_col}
                FROM `{self.DBPath}`
                {where_clause.clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for distinct {mode} versions:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query, job_config=cfg)
            except BadRequest as err:
                Logger.Log(f"In _availableVersions, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row[version_col]) for row in data]
                Logger.Log(f"Found {len(ret_val)} {mode} versions. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} versions from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    def _getEventRows(self, id_filter:IDFilterCollection, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection, event_filter:EventFilterCollection) -> List[Tuple]:
        ret_val = []

        if self.Connector.Client:
            # 1. Create query & config
            where_clause : ParamaterizedClause = self._generateWhereClause(id_filter=id_filter, date_filter=date_filter, version_filter=version_filter, event_filter=event_filter)
            # TODO Order by user_id, and by timestamp within that.
            # Note that this could prove to be wonky when we have more games without user ids,
            # will need to really rethink this when we start using new system.
            # Still, not a huge deal because most of these will be rewritten at that time anyway.
            query = f"""
                SELECT *
                FROM `{self.DBPath}`
                {where_clause.clause}
                ORDER BY `user_id`, `session_id`, `event_sequence_index` ASC
            """
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for rows from IDs:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query, job_config=cfg)
            except BadRequest as err:
                Logger.Log(f"In _rowsFromIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                Logger.Log(f"...Query yielded results, with query in state: {data.state}", logging.DEBUG, depth=3)
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
        else:
            Logger.Log(f"Can't retrieve collection of events from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)

        return ret_val

    def _getFeatureRows(self, id_filter:IDFilterCollection, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection) -> List[Tuple]:
        return []

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _generateSuffixClause(date_filter:TimingFilterCollection) -> ParamaterizedClause:
        clause = ""
        params = []
        
        if date_filter.TimestampFilter and date_filter.TimestampFilter.Min and date_filter.TimestampFilter.Max:
            str_min, str_max = date_filter.TimestampFilter.Min.strftime("%Y%m%d"), date_filter.TimestampFilter.Max.strftime("%Y%m%d")
            clause = "_TABLE_SUFFIX BETWEEN @suffixstart AND @suffixend"
            params.append(
                bigquery.ScalarQueryParameter(type_="STRING", value=str_min, name="suffixstart")
            )
            params.append(
                bigquery.ScalarQueryParameter(type_="STRING", value=str_max, name="suffixend")
            )
        
        return ParamaterizedClause(clause=clause, params=params)

    @staticmethod
    def _generateWhereClause(id_filter:IDFilterCollection, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection, event_filter:EventFilterCollection) -> ParamaterizedClause:
        exclude : LiteralString

        sess_clause : Optional[LiteralString] = None
        sess_param  : List[bigquery.ArrayQueryParameter] = []
        if id_filter.SessionFilter and len(id_filter.SessionFilter.AsSet) > 0:
            exclude = "NOT" if id_filter.SessionFilter.FilterMode == FilterMode.EXCLUDE else ""
            sess_clause = f"`session_id` {exclude} IN @session_list"
            sess_param.append(
                bigquery.ArrayQueryParameter(name="session_list", array_type="STRING", values=id_filter.SessionFilter.AsList)
            )

        users_clause : Optional[LiteralString] = None
        users_param  : List[bigquery.ArrayQueryParameter] = []
        if id_filter.PlayerFilter and len(id_filter.PlayerFilter.AsSet) > 0:
            exclude = "NOT" if id_filter.PlayerFilter.FilterMode == FilterMode.EXCLUDE else ""
            users_clause = f"`user_id` {exclude} IN @user_list"
            users_param.append(
                bigquery.ArrayQueryParameter(name="user_list", array_type="STRING", values=id_filter.PlayerFilter.AsList)
            )

        times_clause : Optional[LiteralString] = None
        times_param  : List[bigquery.RangeQueryParameter | bigquery.ScalarQueryParameter] = []
        if date_filter.TimestampFilter:
            if date_filter.TimestampFilter.Min and date_filter.TimestampFilter.Max:
                exclude = "NOT" if date_filter.TimestampFilter.FilterMode == FilterMode.EXCLUDE else ""
                times_clause = f"`client_time` {exclude} BETWEEN @timestamp_range"
                times_param.append(
                    bigquery.RangeQueryParameter(name="timestamp_range", range_element_type="TIMESTAMP", start=date_filter.TimestampFilter.Min, end=date_filter.TimestampFilter.Max)
                )
            elif date_filter.TimestampFilter.Min:
                exclude = "<" if date_filter.TimestampFilter.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                times_clause = f"`client_time` {exclude} @timestamp_min"
                times_param.append(
                    bigquery.ScalarQueryParameter(name="timestamp_min", type_="TIMESTAMP", value=date_filter.TimestampFilter.Min)
                )
            else: # date_filter.TimestampFilter.Max is not None
                exclude = ">" if date_filter.TimestampFilter.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                times_clause = f"`client_time` {exclude} @timestamp_max"
                times_param.append(
                    bigquery.ScalarQueryParameter(name="timestamp_max", type_="TIMESTAMP", value=date_filter.TimestampFilter.Max)
                )

        indices_clause : Optional[LiteralString] = None
        indices_param  : List[bigquery.ArrayQueryParameter] = []
        if date_filter.SessionIndexFilter and len(date_filter.SessionIndexFilter.AsSet) > 0:
            exclude = "NOT" if date_filter.SessionIndexFilter.FilterMode == FilterMode.EXCLUDE else ""
            indices_clause = f"`event_session_index` {exclude} IN @sess_index_list"
            indices_param.append(
                bigquery.ArrayQueryParameter(name="sess_index_list", array_type="INT64", values=date_filter.SessionIndexFilter.AsList)
            )

        log_clause : Optional[LiteralString] = None
        log_param  : List[BigQueryParameter] = []
        if version_filter.LogVersionFilter:
            if isinstance(version_filter.LogVersionFilter, SetFilter) and len(version_filter.LogVersionFilter.AsSet) > 0:
                exclude = "NOT" if version_filter.LogVersionFilter.FilterMode == FilterMode.EXCLUDE else ""
                log_clause = f"`log_version` {exclude} IN @log_versions"
                log_param.append(
                    bigquery.ArrayQueryParameter(name="log_versions", array_type="INT64", values=version_filter.LogVersionFilter.AsList)
                )
            elif isinstance(version_filter.LogVersionFilter, RangeFilter):
                if version_filter.LogVersionFilter.Min and version_filter.LogVersionFilter.Max:
                    exclude = "NOT" if version_filter.LogVersionFilter.FilterMode == FilterMode.EXCLUDE else ""
                    log_clause = f"`log_version` {exclude} BETWEEN @log_version_min AND @log_version_max"
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value=str(version_filter.LogVersionFilter.Min))
                    )
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value=str(version_filter.LogVersionFilter.Max))
                    )
                elif version_filter.LogVersionFilter.Min:
                    exclude = "<" if version_filter.LogVersionFilter.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    log_clause = f"`log_version` {exclude} @log_version_min"
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value=str(version_filter.LogVersionFilter.Min))
                    )
                else: # version_filter.LogVersionFilter.Max is not None
                    exclude = ">" if version_filter.LogVersionFilter.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    log_clause = f"`log_version` {exclude} @log_version_max"
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value=str(version_filter.LogVersionFilter.Max))
                    )

        app_clause : Optional[LiteralString] = None
        app_param  : List[BigQueryParameter] = []
        if version_filter.AppVersionFilter:
            if isinstance(version_filter.AppVersionFilter, SetFilter) and len(version_filter.AppVersionFilter.AsSet) > 0:
                exclude = "NOT" if version_filter.AppVersionFilter.FilterMode == FilterMode.EXCLUDE else ""
                app_clause = f"`app_version` {exclude} IN @app_versions"
                app_param.append(
                    bigquery.ArrayQueryParameter(name="app_versions", array_type="INT64", values=version_filter.AppVersionFilter.AsList)
                )
            elif isinstance(version_filter.AppVersionFilter, RangeFilter):
                if version_filter.AppVersionFilter.Min and version_filter.AppVersionFilter.Max:
                    exclude = "NOT" if version_filter.AppVersionFilter.FilterMode == FilterMode.EXCLUDE else ""
                    app_clause = f"`app_version` {exclude} BETWEEN @app_version_range"
                    app_param.append(
                        bigquery.RangeQueryParameter(name="app_version_range", range_element_type="INT64", start=version_filter.AppVersionFilter.Min, end=version_filter.AppVersionFilter.Max)
                    )
                elif version_filter.AppVersionFilter.Min:
                    exclude = "<" if version_filter.AppVersionFilter.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    app_clause = f"`app_version` {exclude} @app_version_min"
                    app_param.append(
                        bigquery.ScalarQueryParameter(name="app_version_min", type_="STRING", value=str(version_filter.AppVersionFilter.Min))
                    )
                else: # version_filter.AppVersionFilter.Max is not None
                    exclude = ">" if version_filter.AppVersionFilter.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    app_clause = f"`app_version` {exclude} @app_version_max"
                    app_param.append(
                        bigquery.ScalarQueryParameter(name="app_version_max", type_="STRING", value=str(version_filter.AppVersionFilter.Max))
                    )

        branch_clause : Optional[LiteralString] = None
        branch_param  : List[BigQueryParameter] = []
        if version_filter.AppBranchFilter:
            if isinstance(version_filter.AppBranchFilter, SetFilter) and len(version_filter.AppBranchFilter.AsSet) > 0:
                exclude = "NOT" if version_filter.AppBranchFilter.FilterMode == FilterMode.EXCLUDE else ""
                app_clause = f"`app_branch` {exclude} IN @app_branchs"
                app_param.append(
                    bigquery.ArrayQueryParameter(name="app_branchs", array_type="INT64", values=version_filter.AppBranchFilter.AsList)
                )
            elif isinstance(version_filter.AppBranchFilter, RangeFilter):
                if version_filter.AppBranchFilter.Min and version_filter.AppBranchFilter.Max:
                    exclude = "NOT" if version_filter.AppBranchFilter.FilterMode == FilterMode.EXCLUDE else ""
                    branch_clause = f"`app_branch` {exclude} BETWEEN @app_branch_range"
                    branch_param.append(
                        bigquery.RangeQueryParameter(name="app_branch_range", range_element_type="INT64", start=version_filter.AppBranchFilter.Min, end=version_filter.AppBranchFilter.Max)
                    )
                elif version_filter.AppBranchFilter.Min:
                    exclude = "<" if version_filter.AppBranchFilter.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    branch_clause = f"`app_branch` {exclude} @app_branch_min"
                    branch_param.append(
                        bigquery.ScalarQueryParameter(name="app_branch_min", type_="STRING", value=str(version_filter.AppBranchFilter.Min))
                    )
                else: # version_filter.AppBranchFilter.Max is not None
                    exclude = ">" if version_filter.AppBranchFilter.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    branch_clause = f"`app_branch` {exclude} @app_branch_max"
                    branch_param.append(
                        bigquery.ScalarQueryParameter(name="app_branch_max", type_="STRING", value=str(version_filter.AppBranchFilter.Max))
                    )

        events_clause : Optional[LiteralString] = None
        events_param  : List[bigquery.ArrayQueryParameter] = []
        if event_filter.EventNameFilter and len(event_filter.EventNameFilter.AsSet) > 0:
            exclude = "NOT" if event_filter.EventNameFilter.FilterMode == FilterMode.EXCLUDE else ""
            events_clause = f"`event_name` {exclude} IN @event_name_list"
            events_param.append(
                bigquery.ArrayQueryParameter(name="event_name_list", array_type="STRING", values=event_filter.EventNameFilter.AsList)
            )

        # codes_clause : Optional[LiteralString] = None
        # codes_param  : List[BigQueryParameter] = []
        # if event_filter.EventCodeFilter:
        #     if isinstance(event_filter.EventCodeFilter, SetFilter) and len(event_filter.EventCodeFilter.AsSet) > 0:
        #         exclude = "NOT" if event_filter.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ""
        #         codes_clause = f"`event_code` {exclude} IN @app_branchs"
        #         codes_param.append(
        #             bigquery.ArrayQueryParameter(name="app_branchs", array_type="INT64", values=event_filter.EventCodeFilter.AsList)
        #         )
        #     elif isinstance(event_filter.EventCodeFilter, RangeFilter):
        #         if event_filter.EventCodeFilter.Min and event_filter.EventCodeFilter.Max:
        #             exclude = "NOT" if event_filter.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ""
        #             codes_clause = f"`event_code` {exclude} BETWEEN @event_codes_range"
        #             codes_param.append(
        #                 bigquery.RangeQueryParameter(name="event_codes_range", range_element_type="INT64", start=event_filter.EventCodeFilter.Min, end=event_filter.EventCodeFilter.Max)
        #             )
        #         elif event_filter.EventCodeFilter.Min:
        #             exclude = "<" if event_filter.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
        #             codes_clause = f"`event_code` {exclude} @event_codes_min"
        #             codes_param.append(
        #                 bigquery.ScalarQueryParameter(name="event_codes_min", type_="STRING", value=str(event_filter.EventCodeFilter.Min))
        #             )
        #         else: # event_filter.EventCodeFilter.Max is not None
        #             exclude = ">" if event_filter.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
        #             codes_clause = f"`event_code` {exclude} @event_codes_max"
        #             codes_param.append(
        #                 bigquery.ScalarQueryParameter(name="event_codes_max", type_="STRING", value=str(event_filter.EventCodeFilter.Max))
        #             )

        clause_list_raw : List[Optional[LiteralString]] = [sess_clause, users_clause, times_clause, indices_clause, log_clause, app_clause, branch_clause, events_clause, codes_clause]
        clause_list     : List[LiteralString]           = [clause for clause in clause_list_raw if clause is not None]
        where_clause    : LiteralString                 = f"WHERE {'\nAND '.join(clause_list)}" if len(clause_list) > 0 else ""

        # params_collection = [sess_param, users_param, times_param, indices_param, log_param, app_param, branch_param, events_param, codes_param]
        params_collection = [sess_param, users_param, times_param, indices_param, log_param, app_param, branch_param, events_param]
        params = list(chain.from_iterable(params_collection))

        return ParamaterizedClause(clause=where_clause, params=params)

    # *** PRIVATE METHODS ***
