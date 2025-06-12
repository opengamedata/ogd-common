## import standard libraries
import abc
import logging
from datetime import datetime, timezone
from typing import List, Optional, Union
# import local files
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class GameData
class GameData(abc.ABC):
    """
    Completely dumb struct that enforces a particular structure for the data we get from a source.
    This acts as a common starting point for the `Event` and `FeatureData` classes, defining the common elements between the two.

    TODO : Consider whether to inherit from Schema. Would at least be good to have FromDict as a required function
    """

    @staticmethod
    @abc.abstractmethod
    def ColumnNames() -> List[str]:
        pass

    @abc.abstractmethod
    def ColumnValues(self) -> List[Union[str, datetime, timezone, Map, int, None]]:
        """A list of all values for the row, in order they appear in the `ColumnNames` function.

        .. todo:: Technically, this should be string representations of each, but we're technically not enforcing that yet.
        .. todo:: Currently assuming a single app/log version, but theoretically we could, for example, have multiple app versions show up in a single population. Need to handle this, e.g. allow a list.

        :return: The list of values.
        :rtype: List[Union[str, datetime, timezone, Map, int, None]]
        """
        pass

    def __init__(self, app_id:str,          user_id:Optional[str],          session_id:str,
                 app_version:Optional[str], app_branch:Optional[str],       log_version:Optional[str]):
        """Constructor for a GameData struct.

        :param app_id: _description_
        :type app_id: str
        :param user_id: _description_
        :type user_id: Optional[str]
        :param session_id: _description_
        :type session_id: str
        :param app_version: _description_
        :type app_version: Optional[str]
        :param app_branch: _description_
        :type app_branch: Optional[str]
        :param log_version: _description_
        :type log_version: Optional[str]
        """
        # TODO: event source, e.g. from game or from detector
        self.app_id               : str           = app_id
        self.user_id              : Optional[str] = user_id
        self.session_id           : str           = session_id
        self.app_version          : str           = app_version if app_version is not None else "0"
        self.app_branch           : str           = app_branch  if app_branch  is not None else "main"
        self.log_version          : str           = log_version if log_version is not None else "0"

    @staticmethod
    def CompareVersions(a:str, b:str, version_separator='.') -> int:
        a_parts : Optional[List[int]]
        b_parts : Optional[List[int]]
        try:
            a_parts = [int(i) for i in a.split(version_separator)]
        except ValueError:
            a_parts = None
        try:
            b_parts = [int(i) for i in b.split(version_separator)]
        except ValueError:
            b_parts = None

        if a_parts is not None and b_parts is not None:
            for i in range(0, min(len(a_parts), len(b_parts))):
                if a_parts[i] < b_parts[i]:
                    return -1
                elif a_parts[i] > b_parts[i]:
                    return 1
            if len(a_parts) < len(b_parts):
                return -1
            elif len(a_parts) > len(b_parts):
                return 1
            else:
                return 0
        else:
            # try to do some sort of sane handling in case we got null values for a version
            if a_parts is None and b_parts is None:
                Logger.Log(f"Got invalid values of {a} & {b} for versions a & b!", logging.ERROR)
                return 0
            elif a_parts is None:
                Logger.Log(f"Got invalid value of {a} for version a!", logging.ERROR)
                return 1
            elif b_parts is None:
                Logger.Log(f"Got invalid value of {b} for version b!", logging.ERROR)
                return -1
        return 0 # should never reach here; just putting this here to satisfy linter

    @property
    def AppID(self) -> str:
        """The Application ID of the game that generated the Event

        Generally, this will be the game's name, or some abbreviation of the name.

        :return: The Application ID of the game that generated the Event
        :rtype: str
        """
        return self.app_id

    @property
    def SessionID(self) -> str:
        """The Session ID of the session that generated the Event

        Generally, this will be a numeric string.
        Every session ID is unique (with high probability) from all other sessions.

        :return: The Session ID of the session that generated the Event
        :rtype: str
        """
        return self.session_id

    @property
    def PlayerID(self) -> Optional[str]:
        """Syntactic sugar for the UserID property:
        
        A persistent ID for a given user, identifying the individual across multiple gameplay sessions
        This identifier is only included by games with a mechanism for individuals to resume play in a new session.

        :return: A persistent ID for a given user, identifying the individual across multiple gameplay sessions
        :rtype: Optional[str]
        """
        return self.user_id

    @property
    def UserID(self) -> Optional[str]:
        """A persistent ID for a given user, identifying the individual across multiple gameplay sessions

        This identifier is only included by games with a mechanism for individuals to resume play in a new session.

        :return: A persistent ID for a given user, identifying the individual across multiple gameplay sessions
        :rtype: Optional[str]
        """
        return self.user_id

    @property
    def AppVersion(self) -> str:
        """The semantic versioning string for the game that generated this Event.

        Some legacy games may use a single integer or a string similar to AppID in this column.

        :return: The semantic versioning string for the game that generated this Event
        :rtype: str
        """
        return self.app_version

    @property
    def AppBranch(self) -> str:
        """The name of the branch of a game version that generated this Event.

        The branch name is typically used for cases where multiple experimental versions of a game are deployed in parallel;
        most events will simply have a branch of "main" or "master."

        :return: The name of the branch of a game version that generated this Event
        :rtype: str
        """
        return self.app_branch

    @property
    def LogVersion(self) -> str:
        """The version of the logging schema implemented in the game that generated the Event

        For most games, this is a single integer; however, semantic versioning is valid for this column as well.

        :return: The version of the logging schema implemented in the game that generated the Event
        :rtype: str
        """
        return self.log_version
