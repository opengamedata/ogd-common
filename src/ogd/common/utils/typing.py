## import standard libraries
import builtins
import json
import logging
import re
import datetime
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, TypeAlias, Type
## import 3rd-party libraries
from dateutil import parser
## import local files
from ogd.common.utils.Logger import Logger

Map       : TypeAlias = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"
ExportRow : TypeAlias = List[Any]

class conversions:

    # *** PUBLIC STATICS ***

    @staticmethod
    def ConvertToType(value:Any, to_type:str | Type | List[Type], name:str) -> Any:
        """Applies whatever parsing is appropriate based on what type the schema said a column contained.

        :param value: _description_
        :type value: Any
        :param to_type: The desired type of the element.
            * If a string, the function will match against a set of recognized type names.
            * If a type, the function will match against a set of recognized types.
            * If a list of types, the function will attempt to match the raw value's type against all types in the list.  
                If a match is found, where "match" means the raw value is an instance of the given type, the return value will be the same type as the raw value.  
                If the raw value's type matches nothing in the list, the return value will be a parsed instance of the first type in the list.
                The function naively assumes the first type in the list is a recognized type; if it is not, a value of None will be returned.
        :type to_type: str | Type | List[Type]
        :param name: _description_
        :type name: str
        :return: _description_
        :rtype: Any
        """
        ret_val : Any

        if value is None:
            ret_val = None
        elif value == "None" or value == "null" or value == "nan":
            ret_val = None
        elif isinstance(to_type, str):
            match (to_type.upper()):
                case 'BOOL':
                    ret_val = conversions._parseBool(name=name, value=value)
                case 'STR':
                    ret_val = conversions._parseString(value=value, name=name)
                case 'INT':
                    ret_val = conversions._parseInt(value=value, name=name)
                case 'FLOAT':
                    ret_val = conversions._parseFloat(value=value, name=name)
                case 'DATETIME':
                    ret_val = conversions._parseDatetime(value=value, name=name)
                case 'TIMEDELTA':
                    ret_val = conversions._parseTimedelta(value=value, name=name)
                case 'TIMEZONE':
                    ret_val = conversions._parseTimezone(value=value, name=name)
                case 'JSON':
                    ret_val = conversions._parseJSON(value=value, name=name)
                case _dummy if _dummy.startswith('ENUM'):
                    # if the column is supposed to be an enum, for now we just stick with the string.
                    ret_val = str(value)
                case _:
                    _msg = f"Requested type of {to_type} for '{name}' is unknown; defaulting to {name}=None"
                    Logger.Log(_msg, logging.WARNING)
                    ret_val = None
        elif isinstance(to_type, Type):
            match (to_type):
                case builtins.bool:
                    ret_val = conversions._parseBool(name=name, value=value)
                case builtins.int:
                    ret_val = conversions._parseInt(name=name, value=value)
                case builtins.float:
                    ret_val = conversions._parseFloat(name=name, value=value)
                case builtins.str:
                    ret_val = conversions._parseString(name=name, value=value)
                case datetime.datetime:
                    ret_val = conversions._parseDatetime(value=value, name=name)
                case datetime.timedelta:
                    ret_val = conversions._parseTimedelta(value=value, name=name)
                case datetime.timezone:
                    ret_val = conversions._parseTimezone(value=value, name=name)
                case builtins.dict:
                    ret_val = conversions._parseJSON(value=value, name=name)
                case _:
                    _msg = f"Requested type of {to_type} for '{name}' is unknown; defaulting to {name}=None"
                    Logger.Log(_msg, logging.WARN)
                    ret_val = None
        # Handle case where there are multiple valid types accepted (i.e. got a list, and everything in list is a type/str)
        elif isinstance(to_type, List) and all(type(x) in {type, str} for x in to_type):
            _found = False
            for t in to_type:
                if isinstance(value, t):
                    ret_val = value
                    _found = True
            if not _found:
                ret_val = conversions.ConvertToType(value, to_type=to_type[0], name=name)
        else:
            ret_val = None
        return ret_val

    @staticmethod
    def DatetimeFromString(time_str:str) -> datetime.datetime:
        ret_val : datetime.datetime

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
                ret_val = datetime.datetime.strptime(time_str, fmt)
            except ValueError:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timestamp {time_str}, it did not match any expected formats!")

    @staticmethod
    def TimedeltaFromString(time_str:str) -> Optional[datetime.timedelta]:
        ret_val : Optional[datetime.timedelta]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"\d+:\d+:\d+(\.\d+)?", string=time_str):
            try:
                pieces = time_str.split(':')
                seconds_pieces = pieces[2].split('.')
                ret_val = datetime.timedelta(hours=int(pieces[0]),
                                    minutes=int(pieces[1]),
                                    seconds=int(seconds_pieces[0]),
                                    milliseconds=int(seconds_pieces[1]) if len(seconds_pieces) > 1 else 0)
            except ValueError:
                pass
            except IndexError:
                pass
            else:
                return ret_val
        elif re.fullmatch(pattern=r"-?\d+", string=time_str):
            try:
                ret_val = datetime.timedelta(seconds=int(time_str))
            except ValueError:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timedelta {time_str} of type {type(time_str)}, it did not match any expected formats.")

    @staticmethod
    def TimezoneFromString(time_str:str) -> Optional[datetime.timezone]:
        ret_val : Optional[datetime.timezone]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"UTC[+-]\d+:\d+", string=time_str):
            try:
                pieces = time_str.removeprefix("UTC").split(":")
                ret_val = datetime.timezone(datetime.timedelta(hours=int(pieces[0]), minutes=int(pieces[1])))
            except ValueError:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timezone {time_str} of type {type(time_str)}, it did not match any expected formats.")

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseBool(name:str, value:Any) -> bool:
        ret_val : bool
        match type(value):
            case builtins.bool:
                ret_val = value
            case builtins.int | builtins.float:
                ret_val = bool(value)
            case builtins.str:
                ret_val = True if value.upper() in {'TRUE', 'YES'} else False if value.upper() in {'FALSE', 'NO'} else bool(value)
            case _:
                ret_val = bool(value)
                Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to bool(value) == {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseInt(name:str, value:Any) -> int:
        ret_val : int
        match type(value):
            case builtins.int:
                ret_val = value
            case builtins.float:
                ret_val = int(round(value))
                Logger.Log(f"{name} was a float value, rounding to nearest int: {ret_val}.", logging.WARN)
            case _:
                ret_val = int(value)
                Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to int(value) == {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseFloat(name:str, value:Any) -> float:
        ret_val : float
        match type(value):
            case builtins.float:
                ret_val = value
            case builtins.int:
                ret_val = float(value)
            case _:
                ret_val = int(value)
                Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to float(value) == {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseString(name:str, value:Any) -> str:
        ret_val : str
        match type(value):
            case builtins.str:
                ret_val = value
            case _:
                ret_val = str(value)
                Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to str(value) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDatetime(name:str, value:Any) -> datetime.datetime:
        ret_val : datetime.datetime
        match type(value):
            case datetime.datetime:
                ret_val = value
            case datetime.date:
                midnight = datetime.datetime.min.time()
                ret_val = datetime.datetime.combine(date=value, time=midnight)
                Logger.Log(f"{name} was a date value, defaulting to midnight of the given date: {ret_val}", logging.WARN)
            case builtins.str:
                ret_val = conversions.DatetimeFromString(time_str=value)
            case _:
                ret_val = conversions.DatetimeFromString(str(value))
                Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to datetime(str(value)) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTimedelta(value:Any, name:str) -> Optional[datetime.timedelta]:
        ret_val : Optional[datetime.timedelta]
        match type(value):
            case datetime.timedelta:
                ret_val = value
            case datetime.time:
                ret_val = value - datetime.datetime.min.time()
                Logger.Log(f"{name} was a time value, treating the time is difference from 0: {ret_val}", logging.WARN)
            case builtins.str:
                ret_val = conversions.TimedeltaFromString(time_str=value)
            case _:
                ret_val = conversions.TimedeltaFromString(str(value))
                Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to timedelta(str(value)) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTimezone(value:Any, name:str) -> Optional[datetime.timezone]:
        ret_val : Optional[datetime.timezone]
        match type(value):
            case datetime.timezone:
                ret_val = value
            case builtins.str:
                ret_val = conversions.TimezoneFromString(time_str=value)
            case _:
                ret_val = conversions.TimezoneFromString(str(value))
                Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to timezone(str(value)) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseJSON(value:Any, name:str) -> Optional[Dict]:
        ret_val : Optional[Dict]
        try:
            match type(value):
                case builtins.dict:
                    # if input was a dict already, then just give it back. Else, try to load it from string.
                    ret_val = value
                case builtins.str:
                    if value != 'None' and value != '': # watch out for nasty corner cases.
                        ret_val = json.loads(value)
                    else:
                        ret_val = None
                case _:
                    ret_val = json.loads(str(value))
                    Logger.Log(f"{name} was unexpected type {type(value)}, defaulting to json.parse(str(value)) == {ret_val}", logging.WARN)
        except JSONDecodeError as err:
            Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to JSON, got the following error:\n{str(err)}", logging.WARN)
            ret_val = {}
        return ret_val

    # *** PRIVATE METHODS ***
