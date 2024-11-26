"""DataInterface Module
"""
## import standard libraries
import abc
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# import local files
from ogd.common.connectors.filters.collections import *
from ogd.common.connectors.StorageConnector import StorageConnector
from ogd.common.models.Event import Event
from ogd.common.models.FeatureData import FeatureData
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.schemas.configs.GameSourceSchema import GameSourceSchema
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.utils.SemanticVersion import SemanticVersion
from ogd.common.utils.Logger import Logger

class Interface(StorageConnector):
    """Base class for all connectors that serve as an interface to some IO resource.

    All subclasses must implement the `_availableIDs`, `_availableDates`, `_IDsFromDates`, and `_datesFromIDs` functions.
    """

    # *** ABSTRACTS ***

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
    def _getEventCollection(self, schema:EventTableSchema, id_filter:IDFilterCollection, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection, event_filter:EventFilterCollection) -> List[Event]:
        pass

    @abc.abstractmethod
    def _getFeatureCollection(self, schema:FeatureTableSchema, id_filter:IDFilterCollection, date_filter:TimingFilterCollection, version_filter:VersioningFilterCollection) -> List[FeatureData]:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, schema:GameSourceSchema):
        super().__init__(schema=schema)

    def __del__(self):
        self.Close()

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
        if self.IsOpen:
            _date_clause = f" on date(s) {date_filter}"
            _version_clause = f" with version(s) {version_filter}"
            _msg = f"Retrieving IDs with {mode} ID mode{_date_clause}{_version_clause} from {self.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableIDs(mode=mode, date_filter=date_filter, version_filter=version_filter)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
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
        if self.IsOpen:
            _version_clause = f" with version(s) {version_filter}"
            _msg = f"Retrieving range of event/feature dates{_version_clause} from {self.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableDates(id_filter=id_filter, version_filter=version_filter)
        else:
            Logger.Log(f"Could not get full date range from {self.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
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
        if self.IsOpen:
            _date_clause = f" on date(s) {date_filter}"
            _msg = f"Retrieving data versions{_date_clause} from {self.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableVersions(mode=mode, id_filter=id_filter, date_filter=date_filter)
        else:
            Logger.Log(f"Could not retrieve data versions from {self.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return ret_val

    def GetEventCollection(self, schema:EventTableSchema, id_filter:IDFilterCollection=IDFilterCollection(), date_filter:TimingFilterCollection=TimingFilterCollection(), version_filter:VersioningFilterCollection=VersioningFilterCollection(), event_filter:EventFilterCollection=EventFilterCollection()) -> List[Event]:
        return self._getEventCollection(schema=schema, id_filter=id_filter, date_filter=date_filter, version_filter=version_filter, event_filter=event_filter)

    def GetFeatureCollection(self, schema:FeatureTableSchema, id_filter:IDFilterCollection=IDFilterCollection(), date_filter:TimingFilterCollection=TimingFilterCollection(), version_filter:VersioningFilterCollection=VersioningFilterCollection()) -> List[FeatureData]:
        return self._getFeatureCollection(schema=schema, id_filter=id_filter, date_filter=date_filter, version_filter=version_filter)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
