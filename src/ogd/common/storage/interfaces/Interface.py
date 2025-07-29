"""DataInterface Module
"""
## import standard libraries
import abc
import logging
from datetime import datetime
from pprint import pformat
from typing import Dict, List, Optional, Tuple, Union

# import local files
from ogd.common.filters.collections import *
from ogd.common.storage.StorageConnector import StorageConnector
from ogd.common.models.Event import Event
from ogd.common.models.EventDataset import EventDataset
from ogd.common.models.Feature import Feature
from ogd.common.models.FeatureDataset import FeatureDataset
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.utils.Logger import Logger

class Interface(abc.ABC):
    """Base class for all connectors that serve as an interface to some IO resource.

    All subclasses must implement the `_availableIDs`, `_availableDates`, `_IDsFromDates`, and `_datesFromIDs` functions.
    """

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Connector(self) -> StorageConnector:
        pass

    @abc.abstractmethod
    def _availableIDs(self, mode:IDMode, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection) -> List[str]:
        """Private implementation of the logic to retrieve all IDs of given mode from the connected storage.

        :param mode: The type of ID to be listed.
        :type mode: IDMode
        :return: A list of IDs with given mode available through the connected storage.
        :rtype: List[str]
        """
        pass

    @abc.abstractmethod
    def _availableDates(self, id_filter:IDFilterCollection, version_filter:VersioningFilterCollection) -> Dict[str,datetime]:
        """Private implementation of the logic to retrieve the full range of dates/times from the connected storage.

        :return: A dict mapping `min` and `max` to the minimum and maximum datetimes
        :rtype: Dict[str,datetime]
        """
        pass

    @abc.abstractmethod
    def _availableVersions(self, mode:VersionType, id_filter:IDFilterCollection, date_filter:TimingFilterCollection) -> List[SemanticVersion | str]:
        pass

    @abc.abstractmethod
    def _getEventRows(self, id_filter:IDFilterCollection, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection, event_filter:EventFilterCollection) -> List[Tuple]:
        pass

    @abc.abstractmethod
    def _getFeatureRows(self, id_filter:IDFilterCollection, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection) -> List[Tuple]:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, fail_fast:bool):
        self._fail_fast = fail_fast
        self._config = config
        super().__init__()


    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def AvailableIDs(self, mode:IDMode, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection) -> Optional[List[str]]:
        """Retrieve all IDs of given mode from the connected storage.

        :param mode: The type of ID to be listed.
        :type mode: IDMode
        :return: A list of IDs with given mode available through the connected storage.
        :rtype: List[str]
        """
        ret_val = None
        if self.Connector.IsOpen:
            _msg = f"Retrieving IDs with {mode} ID mode on date(s) {date_filter} with version(s) {version_filter} from {self.Connector.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableIDs(mode=mode, date_filter=date_filter, version_filter=version_filter)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return ret_val

    def AvailableDates(self, id_filter:IDFilterCollection, version_filter:VersioningFilterCollection) -> Union[Dict[str,datetime], Dict[str,None]]:
        """Retrieve the full range of dates/times covered by data in the connected storage, subject to given filters.

        Note, this is different from listing the exact dates in which the data exists.
        This function gets the range from the earliest instance of an event matching the filters, to the last such instance.

        TODO: Create separate functions for exact dates and date range.

        :return: A dictionary mapping `min` and `max` to the range of dates covering all data for the given IDs/versions
        :rtype: Union[Dict[str,datetime], Dict[str,None]]
        """
        ret_val = {'min':None, 'max':None}
        if self.Connector.IsOpen:
            _msg = f"Retrieving range of event/feature dates with version(s) {version_filter} from {self.Connector.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableDates(id_filter=id_filter, version_filter=version_filter)
        else:
            Logger.Log(f"Could not get full date range from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return ret_val


    def AvailableVersions(self, mode:VersionType, id_filter:IDFilterCollection, date_filter:TimingFilterCollection) -> List[SemanticVersion | str]:
        """Get a list of all versions of given type in the connected storage, subject to ID and date filters.

        :param mode: _description_
        :type mode: VersionType
        :param id_filter: _description_
        :type id_filter: IDFilterCollection
        :param date_filter: _description_
        :type date_filter: TimingFilterCollection
        :return: _description_
        :rtype: List[SemanticVersion | str]
        """
        ret_val = []
        if self.Connector.IsOpen:
            _msg = f"Retrieving data versions on date(s) {date_filter} from {self.Connector.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableVersions(mode=mode, id_filter=id_filter, date_filter=date_filter)
        else:
            Logger.Log(f"Could not retrieve data versions from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return ret_val

    def GetEventCollection(self, id_filter:IDFilterCollection=IDFilterCollection(), date_filter:TimingFilterCollection=TimingFilterCollection(), version_filter:VersioningFilterCollection=VersioningFilterCollection(), event_filter:EventFilterCollection=EventFilterCollection()) -> EventDataset:
        _filters = id_filter.AsDict | date_filter.AsDict | version_filter.AsDict | event_filter.AsDict
        _events = []

        if self.Connector.IsOpen:
            if isinstance(self.GameStoreConfig.TableConfigName, EventTableSchema):
                # _date_clause = f" on date(s) {date_filter}"
                _msg = f"Retrieving event data from {self.Connector.ResourceName}."
                Logger.Log(_msg, logging.INFO, depth=3)
                _rows = self._getEventRows(id_filter=id_filter, date_filter=date_filter, version_filter=version_filter, event_filter=event_filter)
                _events = self._eventsFromRows(rows=_rows)
            else:
                Logger.Log(f"Could not retrieve event data from {self.Connector.ResourceName}, the given table schema was not for event data!", logging.WARNING, depth=3)
        else:
            Logger.Log(f"Could not retrieve event data from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)

        return EventDataset(events=_events, filters=_filters)

    def GetFeatureCollection(self, id_filter:IDFilterCollection=IDFilterCollection(), date_filter:TimingFilterCollection=TimingFilterCollection(), version_filter:VersioningFilterCollection=VersioningFilterCollection()) -> FeatureDataset:
        _filters = id_filter.AsDict | date_filter.AsDict | version_filter.AsDict
        _features = []
        if self.Connector.IsOpen:
            if isinstance(self.GameStoreConfig.TableConfigName, EventTableSchema):
                # _date_clause = f" on date(s) {date_filter}"
                _msg = f"Retrieving event data from {self.Connector.ResourceName}."
                Logger.Log(_msg, logging.INFO, depth=3)
                _rows = self._getFeatureRows(id_filter=id_filter, date_filter=date_filter, version_filter=version_filter)
                _features = self._featuresFromRows(rows=_rows)
            else:
                Logger.Log(f"Could not retrieve event data from {self.Connector.ResourceName}, the given table schema was not for event data!", logging.WARNING, depth=3)
        else:
            Logger.Log(f"Could not retrieve feature data from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return FeatureDataset(features=_features, filters=_filters)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _eventsFromRows(self, rows:List[Tuple]) -> List[Event]:
        ret_val = []

        _curr_sess : str      = ""
        _evt_sess_index : int = 1
        _fallbacks = {"app_id":self._source_schema.GameID}
        _table_schema = self.GameStoreConfig.TableConfigName
        if isinstance(_table_schema, EventTableSchema):
            for row in rows:
                try:
                    event = _table_schema.EventFromRow(row)
                    # in case event index was not given, we should fall back on using the order it came to us.
                    if event.SessionID != _curr_sess:
                        _curr_sess = event.SessionID
                        _evt_sess_index = 1
                    event.FallbackDefaults(index=_evt_sess_index)
                    _evt_sess_index += 1
                except Exception as err:
                    if self._fail_fast:
                            Logger.Log(f"Error while converting row to Event\nFull error: {err}\nRow data: {pformat(row)}", logging.ERROR, depth=2)
                            raise err
                    else:
                        Logger.Log(f"Error while converting row ({row}) to Event. This row will be skipped.\nFull error: {err}", logging.WARNING, depth=2)
                else:
                    ret_val.append(event)
        else:
            Logger.Log(f"Could not convert row data to Events, the given table schema was not for event data!", logging.WARNING, depth=3)
        return ret_val

    def _featuresFromRows(self, rows:List[Tuple]) -> List[Feature]:
        """_summary_

        TODO :implement

        :param rows: _description_
        :type rows: List[Tuple]
        :param schema: _description_
        :type schema: FeatureTableConfig
        :return: _description_
        :rtype: List[Feature]
        """
        return []
