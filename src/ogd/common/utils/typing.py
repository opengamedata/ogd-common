## import standard libraries
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from json.decoder import JSONDecodeError
from typing import Any, Callable, Dict, List, Optional, TypeAlias
## import 3rd-party libraries
from dateutil import parser
## import local files
from ogd.common.utils.Logger import Logger

Map       : TypeAlias = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"
ExportRow : TypeAlias = List[Any]

class conversions:

    @staticmethod
    def ConvertToType(variable:Any, to_type:str) -> Any:
        """Applies whatever parsing is appropriate based on what type the schema said a column contained.

        :param input: _description_
        :type input: str
        :param col_schema: _description_
        :type col_schema: ColumnSchema
        :return: _description_
        :rtype: Any
        """
        if variable is None:
            return None
        if variable == "None" or variable == "null" or variable == "nan":
            return None
        match to_type.upper():
            case 'STR':
                return str(variable)
            case 'INT':
                return int(variable)
            case 'FLOAT':
                return float(variable)
            case 'DATETIME':
                return variable if isinstance(variable, datetime) else conversions.DatetimeFromString(str(variable))
            case 'TIMEDELTA':
                return variable if isinstance(variable, timedelta) else conversions.TimedeltaFromString(str(variable))
            case 'TIMEZONE':
                return variable if isinstance(variable, timezone) else conversions.TimezoneFromString(str(variable))
            case 'JSON':
                try:
                    if isinstance(variable, dict):
                        # if input was a dict already, then just give it back. Else, try to load it from string.
                        return variable
                    elif isinstance(variable, str):
                        if variable != 'None' and variable != '': # watch out for nasty corner cases.
                            return json.loads(variable)
                        else:
                            return None
                    else:
                        return json.loads(str(variable))
                except JSONDecodeError as err:
                    Logger.Log(f"Could not parse input '{variable}' of type {type(variable)} to type {to_type}, got the following error:\n{str(err)}", logging.WARN)
                    return {}
            case _dummy if _dummy.startswith('ENUM'):
                # if the column is supposed to be an enum, for now we just stick with the string.
                return str(variable)
            case _:
                Logger.Log(f"ConvertToType function got an unrecognized type {to_type}, could not complete conversion!", logging.WARNING)

    @staticmethod
    def DatetimeFromString(time_str:str) -> datetime:
        ret_val : datetime

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            raise ValueError(f"Got a non-timestamp value of {time_str} when converting a datetime column from data source!")

        formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S.%f"]

        try:
            ret_val = parser.isoparse(time_str)
        except ValueError:
            # Logger.Log(f"Could not parse time string '{time_str}', got error {err}")
            # raise err
            pass
        else:
            return ret_val
        for fmt in formats:
            try:
                ret_val = datetime.strptime(time_str, fmt)
            except ValueError:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timestamp {time_str}, it did not match any expected formats!")

    @staticmethod
    def TimedeltaFromString(time_str:str) -> Optional[timedelta]:
        ret_val : Optional[timedelta]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"\d+:\d+:\d+(\.\d+)?", string=time_str):
            try:
                pieces = time_str.split(':')
                seconds_pieces = pieces[2].split('.')
                ret_val = timedelta(hours=int(pieces[0]),
                                    minutes=int(pieces[1]),
                                    seconds=int(seconds_pieces[0]),
                                    milliseconds=int(seconds_pieces[1]) if len(seconds_pieces) > 1 else 0)
            except ValueError as err:
                pass
            except IndexError as err:
                pass
            else:
                return ret_val
        elif re.fullmatch(pattern=r"-?\d+", string=time_str):
            try:
                ret_val = timedelta(seconds=int(time_str))
            except ValueError as err:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timedelta {time_str} of type {type(time_str)}, it did not match any expected formats.")

    @staticmethod
    def TimezoneFromString(time_str:str) -> Optional[timezone]:
        ret_val : Optional[timezone]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"UTC[+-]\d+:\d+", string=time_str):
            try:
                pieces = time_str.removeprefix("UTC").split(":")
                ret_val = timezone(timedelta(hours=int(pieces[0]), minutes=int(pieces[1])))
            except ValueError as err:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timezone {time_str} of type {type(time_str)}, it did not match any expected formats.")