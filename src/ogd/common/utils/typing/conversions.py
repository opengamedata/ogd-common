"""Utility class with simple, "common-sense" parsing and warning logs for converting between types.

In particular, this is intended for use by config/schema classes,
where incoming values may be strings that must be parsed into the proper type internally.
"""

## import standard libraries
import builtins
import datetime
import json
import logging
import pathlib
import re
import typing
from abc import ABCMeta
from typing import Any, Dict, List, LiteralString, Optional, Type

from json.decoder import JSONDecodeError
## import 3rd-party libraries
from pandas import Timedelta
from pandas._libs.tslibs import timestamps, timedeltas
from dateutil import parser
## import local files
from ogd.common.utils.helpers import Capitalize
from ogd.common.utils.typing import to
from ogd.common.utils.Logger import Logger

def ConvertToType(value:Any, to_type:str | Type | List[Type], name:str="Unnamed Element", force_conversion:bool=True) -> Any:
    """Function to convert a given value to a specific type, or to one of a list of acceptable types.
    
    Applies whatever parsing is appropriate to convert `value` to the type, or None if the type of `value` was incompatible with the conversion.
    Below is a table of what types are supported as `to_type` targets, and which incoming types are handled when converting to each target type.
    | Target Type | Supported `type(value)`               |
    | ---         | ---                                   |
    | bool        | bool, int, float, str                 |
    | str         | str, any type implementing `__str__`  |
    | int         | int, float, str                       |
    | float       | int, float, str                       |
    | Path        | pathlib.Path, str                     |
    | date        | date, datetime, str, Pandas timestamp |
    | datetime    | date, datetime, str, Pandas timestamp |
    | timedelta   | time, timedelta, str, int, Pandas timedelta |
    | timezone    | timezone, timedelta, str              |
    | dict/json   | dict, str (valid JSON strings)        |
    | list        | List, str                             |

    If the requested conversion type is not in the list above, the original value is returned.

    TODO : Add a "force" param that is passed down to the "force" param of lower-level functions.

    :param value: The value to be converted to the desired type.
    :type value: Any
    :param to_type: The desired type of the element.
        * If a string, the function will match against a set of recognized type names.
        * If a type, the function will match against a set of recognized types.
        * If a list of types, the function will attempt to match the raw value's type against all types in the list.  
            If a match is found, where "match" means the raw value is an instance of the given type, the return value will be the same type as the raw value.  
            If the raw value's type matches nothing in the list, the return value will be a parsed instance of the first type in the list.
            The function naively assumes the first type in the list is a recognized type; if it is not, a value of None will be returned.
    :type to_type: str | Type | List[Type]
    :param name: A human-readable name corresponding to the value being converted, used only for logging. Defaults to "Unnamed Element"
    :type name: str, optional
    :param force_conversion: If True, use additional tricks like converting value to str first, to allow values whose types are not normally handled by the parser of the desired type.
                  If False, only convert if value's type is compatible with the desired type, otherwise return None to indicate failure. Defaults to True
    :type force_conversion: bool, optional
    :return: The result of converting `value` to the desired type, or None if the conversion failed and `force` is set to False.
    :rtype: Any
    """
    def _valid_to_type(to_type):
        return isinstance(to_type, type) or isinstance(to_type, str)

    ret_val : Any

    # 1. short-circuit if we got a value representing null.
    if Capitalize(value) in [None, "NONE", "NULL", "NAN"]:
        ret_val = None
    # 2. Handle case where there are multiple valid types accepted (i.e. got a list, and everything in list is a type/str)
    elif isinstance(to_type, List):
        if not all(_valid_to_type(x) for x in to_type):
            Logger.Log(f"In ConvertToType, some items in list of requested types are not strings or types ({[x for x in to_type if type(x) not in {type, ABCMeta, str}]}). These will be ignored.", logging.DEBUG)
            to_type = [x for x in to_type if _valid_to_type(x)]
        found = False
        # for each candidate type, check if value already had that type
        for t in to_type:
            if isinstance(value, t):
                ret_val = value
                found = True
        # if we didn't find exact match between value and candidate type, make a "soft" parse attempt on each type
        # Also good gracious me it's a mother****ing while loop in Python, oh my days...
        i = 0
        while not found and i < len(to_type):
            _parsed = _parseToType(value=value, to_type=to_type[i], name=name)
            if _parsed is not None:
                ret_val = _parsed
                found = True
            i += 1

        # If none of the parsers knew how to handle the type of value param,
        # force the issue by calling a "hard" conversion on first type in list of candidate types.
        if not found:
            ret_val = _parseToType(value=value, to_type=to_type[0], name=name, force_conversion=force_conversion)
    # 3. Otherwise, handle recognized single types
    else:
        ret_val = _parseToType(value=value, to_type=to_type, name=name, force_conversion=force_conversion)
    return ret_val


def DatetimeFromString(time_str:str) -> Optional[datetime.datetime]:
    """_summary_

    TODO : Move into `time` module
    TODO : handle null inputs!
    TODO : handle more date formats, or something. I dunno, copied this from another area where we were parsing dates.

    :param time_str: _description_
    :type time_str: str
    :raises ValueError: _description_
    :raises ValueError: _description_
    :return: _description_
    :rtype: datetime.datetime
    """
    ret_val : Optional[datetime.datetime] = None

    if time_str == None or time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
        raise ValueError(f"Got a non-timestamp value of {time_str} when converting a datetime column from data source!")

    # Approach 1: use dateutil parser to parse, assuming an iso format
    try:
        ret_val = parser.isoparse(time_str)
    # Approach 2: if dateutil threw error, try using the general parse
    except ValueError:
        Logger.Log(f"Attempted to convert a time string that was not in ISO format: {time_str}, switching to general parser instead!", logging.DEBUG)
        try:
            ret_val = parser.parse(time_str)
        except ValueError:
            Logger.Log(f"Could not parse timestamp {time_str}, it did not match any expected formats!", logging.WARNING)
        else:
            pass
    else:
        pass

    return ret_val

def _parseToType(value:Any, to_type:str | Type, name:str="Unnamed Element", force_conversion:bool=False) -> Any:
    """Private function to attempt to parse a value to a specific type.

    Unlike the main ConvertToType function, however,
    this function will not attempt a conversion if the type of the "value" variable is not recognized, and is not already of the requested type.
    Instead, it will simply return None

    :param value: _description_
    :type value: Any
    :param to_type: _description_
    :type to_type: str | Type | List[Type]
    :param name: _description_
    :type name: str
    :return: _description_
    :rtype: Any
    """
    ret_val : Any

    if Capitalize(value) in [None, "NONE", "NULL", "NAN"]:
        ret_val = None
    # check if value is already of correct type.
    elif isinstance(to_type, Type) and isinstance(value, to_type):
        return value
    elif isinstance(to_type, str) and str(type(value)).upper() == f"<CLASS '{to_type.upper()}'>":
        return value
    else:
        match (Capitalize(to_type)):
            case 'BOOL' | builtins.bool:
                ret_val = to.Bool.convert(name=name, value=value, force=force_conversion)
            case 'STR' | builtins.str:
                ret_val = to.String.convert(name=name, value=value)
            case 'INT' | builtins.int:
                ret_val = to.Int.convert(name=name, value=value, force=force_conversion)
            case 'FLOAT' | builtins.float:
                ret_val = to.Float.convert(name=name, value=value, force=force_conversion)
            case 'PATH' | pathlib.Path:
                ret_val = to.Path.convert(name=name, value=value, force=force_conversion)
            case 'DATE' | datetime.date:
                ret_val  = time.ToDate(name=name, value=value, force=force_conversion)
            case 'DATETIME' | datetime.datetime:
                ret_val = time.ToDatetime(name=name, value=value, force=force_conversion)
            case 'TIMEDELTA' | datetime.timedelta:
                ret_val = time.ToTimedelta(name=name, value=value, force=force_conversion)
            case 'TIMEZONE' | datetime.timezone:
                ret_val = time.ToTimezone(name=name, value=value, force=force_conversion)
            case 'JSON' | 'DICT' | builtins.dict | typing.Dict:
                ret_val = to.JSON.convert(name=name, value=value, force=force_conversion)
            case 'LIST' | builtins.list | typing.List:
                ret_val = to.List.convert(name=name, value=value, force=force_conversion)
            case _dummy if isinstance(_dummy, str) and _dummy.startswith('ENUM'):
                # if the column is supposed to be an enum, for now we just stick with the string.
                ret_val = str(value)
            case _:
                _msg = f"Requested type of {to_type} for '{name}' is unknown; defaulting to {name}=None"
                Logger.Log(_msg, logging.DEBUG)
                ret_val = None
    return ret_val

class time:
    @staticmethod
    def ToDate(name:str, value:Any, force:bool=False) -> Optional[datetime.date]:
        ret_val : Optional[datetime.date]

        if isinstance(value, datetime.date):
            ret_val = value
        else:
            converted = time.ToDatetime(name=name, value=value, force=force)
            ret_val = converted.date() if converted is not None else None
        
        return ret_val

    @staticmethod
    def ToDatetime(name:str, value:Any, force:bool=False) -> Optional[datetime.datetime]:
        """Attempt to turn a given value into a datetime

        Returns None if the value type was not recognized.

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a datetime representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `DatetimeFromString` converter on the string of `value`.
            Defaults to False.
        :type force: bool
        :return: The datetime representation of value, if type of value was recognized, else None
        :rtype: Optional[datetime]
        """
        ret_val : Optional[datetime.datetime]

        match type(value):
            case datetime.datetime:
                ret_val = value
            case datetime.date:
                midnight = datetime.datetime.min.time()
                ret_val = datetime.datetime.combine(date=value, time=midnight)
                Logger.Log(f"{name} was a date value, defaulting to midnight of the given date: {ret_val}", logging.WARN)
            case builtins.str:
                ret_val = DatetimeFromString(time_str=value)
            case timestamps.Timestamp:
                ret_val = value.to_pydatetime()
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a datetime or string!"
                if force:
                    ret_val = DatetimeFromString(str(value))
                    msg = f"{base_msg} Defaulting to DatetimeFromString(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
        return ret_val

    @staticmethod
    def ToTimedelta(name:str, value:Any, force:bool=False) -> Optional[datetime.timedelta]:
        """Attempt to turn a given value into a timedelta

        Returns None if the value type was not recognized.

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a timedelta representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `TimedeltaFromString` converter on the string of `value`.
            Defaults to False.
        :type force: bool
        :return: The timedelta representation of value, if type of value was recognized, else None
        :rtype: Optional[timedelta]
        """
        ret_val : Optional[datetime.timedelta]
        match type(value):
            case datetime.timedelta:
                ret_val = value
            case datetime.time:
                ret_val = value - datetime.datetime.min.time()
                Logger.Log(f"{name} was a time value, treating the time is difference from 0: {ret_val}", logging.WARN)
            case builtins.str:
                ret_val = time.TimedeltaFromString(time_str=value)
            case builtins.int:
                ret_val = datetime.timedelta(seconds=value)
            case timedeltas.Timedelta:
                ret_val = value.to_pytimedelta()
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a timedelta, time, or string!"
                if force:
                    ret_val = time.TimedeltaFromString(str(value))
                    msg = f"{base_msg} Defaulting to TimedeltaFromString(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
        return ret_val

    @staticmethod
    def ToTimezone(name:str, value:Any, force:bool=False) -> Optional[datetime.timezone]:
        """Attempt to turn a given value into a timezone

        .. TODO use timedelta from string, possibly, and then create timezone from the delta

        Returns None if the value type was not recognized.

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a timezone representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `TimezoneFromString` convertor on the string of `value`.
            Defaults to False.
        :type force: bool
        :return: The timezone representation of value, if type of value was recognized, else None
        :rtype: Optional[timezone]
        """
        ret_val : Optional[datetime.timezone]
        match type(value):
            case datetime.timezone:
                ret_val = value
            case datetime.timedelta:
                ret_val = datetime.timezone(value)
            case builtins.str:
                ret_val = time.TimezoneFromString(time_str=value)
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a float, int, or string!"
                if force:
                    ret_val = time.TimezoneFromString(str(value))
                    msg = f"{base_msg} Defaulting to TimezoneFromString(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
        return ret_val

    @staticmethod
    def TimedeltaFromString(time_str:str) -> Optional[datetime.timedelta]:
        """Extract a timedelta from a string, or return None if the string was not a valid timedelta.

        Formats we explicitly support (i.e. formats we unit test against).
        A +/- indicates we test both positive and negative timedeltas with given format:
        * HH:MM:SS.mmmmmm (+/-)
        * D day, HH:MM:SS.mmmmmm (+/-)
        * D days, HH:MM:SS.mmmmmm (+/-)
        * HH:MM (+/-)

        *Note* : Based on the formats above, a string with a single colon (:) will be interpreted as clock time, i.e. hours and minutes.  
        *For Example* : 1:23 will be interpreted as one (1) hour, twenty-three (23) minutes.

        The function will apply the following approaches, with the following priority:
        1. Check if the input string represents a 'null' value of some kind
        2. Apply a regex matching the "D days, HH:MM:SS.mmmm" format, and reasonable derivatives (e.g. HH:MM:SS)
        3. Apply a regex matching against a single integer, interpreted as the number of seconds for the timedelta
        4. Apply timedelta parsing from the `pandas` library, which may catch some formats missed by the regex approaches
        5. Apply general parsing with the `dateutil` library, which may catch some formats missed by the other approaches

        :param time_str: _description_
        :type time_str: str
        :return: _description_
        :rtype: Optional[datetime.timedelta]
        """
        ret_val : Optional[datetime.timedelta]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            ret_val = None
        else:
            # Shoutout @timgeb on stackoverflow for the sweet iterator approach to trying a bunch of parser options.
            # https://stackoverflow.com/questions/62235258/call-functions-until-one-of-them-does-not-return-none
            parsers = [
                time.TimedeltaParser.FromRegex,
                time.TimedeltaParser.FromSeconds,
                time.TimedeltaParser.FromPandas,
                time.TimedeltaParser.FromDateutil
            ]
            parser_iterator = (td for p in parsers if (td := p(time_str)) is not None)
            ret_val = next(parser_iterator, None)
            if ret_val is None:
                Logger.Log(f"Could not parse timedelta '{time_str}' of type {type(time_str)}, it did not match any expected formats.", logging.WARNING)
        
        return ret_val

    @staticmethod
    def TimezoneFromString(time_str:str) -> Optional[datetime.timezone]:
        """Extract a timezone from a string representing an offset from UTC, or return None if the string was not a valid timezone offset.

        Formats we explicitly support (i.e. formats we unit test against).
        A +/- indicates we test both positive and negative timedeltas with given format:
        * HH:MM:SS (+/-)
        * HH:MM (+/-)
        * UTC+HH:MM:SS
        * UTC-HH:MM:SS
        * D day, HH:MM:SS.mmmmmm (+/-)
        * D days, HH:MM:SS.mmmmmm (+/-)

        *Note* : Based on the formats above, a string with a single colon (:) will be interpreted as clock time, i.e. hours and minutes.  
        *For Example* : 1:23 will be interpreted as one (1) hour, twenty-three (23) minutes.

        The function will apply the following approaches, with the following priority:
        1. Check if the input string represents a 'null' value of some kind
        2. Apply a regex matching the "UTC[+/-]D day[s], HH:MM:SS.mmmm" format, and reasonable derivatives (e.g. UTC+HH:MM:SS)
        3. Apply a regex matching against a single integer, interpreted as the number of seconds for the offset from UTC
        4. Apply general parsing with the `conversions.time.TimedeltaFromString(...)` function, to obtain an offset from UTC.
            This may catch some formats missed by the regex approaches.

        :param time_str: _description_
        :type time_str: str
        :return: _description_
        :rtype: Optional[datetime.timedelta]
        """
        ret_val : Optional[datetime.timezone]

        offset : Optional[datetime.timedelta] = None
        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        else:
            # Shoutout @timgeb on stackoverflow for the sweet iterator approach to trying a bunch of parser options.
            # https://stackoverflow.com/questions/62235258/call-functions-until-one-of-them-does-not-return-none
            parsers = [
                time.TimezoneParser.FromRegex,
                time.TimezoneParser.FromSeconds,
                time.TimezoneParser.FromTimedeltaString
            ]
            parser_iterator = (td for p in parsers if (td := p(time_str)) is not None)
            ret_val = next(parser_iterator, None)
            if ret_val is None:
                Logger.Log(f"Could not parse timezone '{time_str}' of type {type(time_str)}, it did not match any expected formats.", logging.WARNING)

            return ret_val

    class TimedeltaParser:

        _PATTERN = None

        @staticmethod
        def PATTERN() -> re.Pattern:
            if time.TimedeltaParser._PATTERN is None:
                neg_pattern    : LiteralString = r"(?P<neg>-)"
                day_pattern    : LiteralString = r"(?:(?P<day>\d+)\s+day(?:s)?,\s+)"
                hour_pattern   : LiteralString = r"(?P<hour>\d+)"
                minute_pattern : LiteralString = r"(?P<minute>\d+)"
                second_pattern : LiteralString = r"(?P<second>\d+)"
                micros_pattern : LiteralString = r"(?P<micros>\d+)"
                time.TimedeltaParser._PATTERN = re.compile(f"{neg_pattern}?{day_pattern}?{hour_pattern}:{minute_pattern}(:{second_pattern}(\\.{micros_pattern})?)?")
            return time.TimedeltaParser._PATTERN

        @staticmethod
        def FromRegex(time_str:str) -> Optional[datetime.timedelta]:
            ret_val = None

            match = re.fullmatch(pattern=time.TimedeltaParser.PATTERN(), string=time_str)
            if match:
                td = datetime.timedelta(
                    days=int(match.group("day") or 0),
                    hours=int(match.group("hour") or 0),
                    minutes=int(match.group("minute") or 0),
                    seconds=int(match.group("second") or 0),
                    microseconds=int(match.group("micros") or 0)
                )
                # if we matched the negative sign, then make the timedelta negative.
                ret_val = td if not match.group("neg") else -td
            return ret_val

        @staticmethod
        def FromSeconds(time_str:str) -> Optional[datetime.timedelta]:
            ret_val = None

            match = re.fullmatch(pattern=r"-?\d+", string=time_str)
            if match:
                ret_val = datetime.timedelta(seconds=int(time_str))

            return ret_val

        @staticmethod
        def FromDateutil(time_str:str) -> Optional[datetime.timedelta]:
            ret_val = None

            try:
                dt = parser.parse(time_str)
            except parser.ParserError:
                pass # if we got a bad string, then fine, we'll just return None
            else:
                td = dt - datetime.datetime.combine(dt.date(), datetime.time.min)
                ret_val = td if not time_str.startswith("-") else -td

            return ret_val

        @staticmethod
        def FromPandas(time_str:str) -> Optional[datetime.timedelta]:
            ret_val = None

            try:
                td = Timedelta(time_str)
            except ValueError:
                pass # if we got a bad string, then fine, we'll just return None
            else:
                ret_val = td.to_pytimedelta()

            return ret_val
    
    class TimezoneParser:

        _PATTERN = None

        @staticmethod
        def PATTERN() -> re.Pattern:
            if time.TimezoneParser._PATTERN is None:
                utc_pattern    : LiteralString = r"(?P<utc>UTC)"
                dir_pattern    : LiteralString = r"(?P<dir>\+|-)"
                day_pattern    : LiteralString = r"(?:(?P<day>\d+)\s+day(?:s)?,\s+)"
                hour_pattern   : LiteralString = r"(?P<hour>\d+)"
                minute_pattern : LiteralString = r"(?P<minute>\d+)"
                second_pattern : LiteralString = r"(?P<second>\d+)"
                micros_pattern : LiteralString = r"(?P<micros>\d+)"
                raw_pattern = f"{utc_pattern}?{dir_pattern}?{day_pattern}?{hour_pattern}:{minute_pattern}:{second_pattern}(\\.{micros_pattern})?"

                time.TimezoneParser._PATTERN = re.compile(raw_pattern)
            return time.TimezoneParser._PATTERN
        
        @staticmethod
        def FromRegex(time_str:str) -> Optional[datetime.timezone]:
            ret_val = None

            match = re.fullmatch(pattern=time.TimezoneParser.PATTERN(), string=time_str)
            if match:
                offset = datetime.timedelta(
                    days=int(match.group("day") or 0),
                    hours=int(match.group("hour") or 0),
                    minutes=int(match.group("minute") or 0),
                    seconds=int(match.group("second") or 0),
                    microseconds=int(match.group("micros") or 0)
                )
                # if we matched the negative sign, then make the timedelta negative.
                if match.group("dir") == "-":
                    offset = -1*offset
                ret_val = time.TimezoneParser._offsetToTimezone(offset=offset)

            return ret_val

        @staticmethod
        def FromSeconds(time_str:str) -> Optional[datetime.timezone]:
            ret_val = None

            match = re.fullmatch(pattern=r"-?\d+", string=time_str)
            if match:
                offset = datetime.timedelta(seconds=int(time_str))
                ret_val = time.TimezoneParser._offsetToTimezone(offset=offset)
            
            return ret_val
        
        @staticmethod
        def FromTimedeltaString(time_str:str) -> Optional[datetime.timezone]:
            ret_val = None

            time_str = time_str.removeprefix("UTC")
            time_str = time_str.removeprefix("+")
            offset = time.TimedeltaFromString(time_str=time_str)
            if offset:
                ret_val = time.TimezoneParser._offsetToTimezone(offset=offset)

            return ret_val

        @staticmethod
        def _offsetToTimezone(offset:datetime.timedelta) -> datetime.timezone:
            """Convert a timedelta offset to a UTC-based timezone

            :param offset: _description_
            :type offset: datetime.timedelta
            :return: _description_
            :rtype: datetime.timezone
            """
            ret_val : datetime.timezone

            MAX_OFFSET = 24*60*60
            if offset.total_seconds() > MAX_OFFSET:
                offset = datetime.timedelta(seconds=offset.total_seconds() % MAX_OFFSET)
            if offset.total_seconds() < -24*60*60:
                offset = datetime.timedelta(seconds=(offset.total_seconds() % MAX_OFFSET) - MAX_OFFSET)

            ret_val = datetime.timezone(offset=offset)

            return ret_val
