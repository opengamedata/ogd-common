## import standard libraries
import abc
import builtins
import datetime
import json
import logging
import pathlib
import pandas
import typing
import re
import typing
from typing import Any, Dict, LiteralString, Optional, Type

from json.decoder import JSONDecodeError
## import 3rd-party libraries
from pandas._libs.tslibs import timestamps, timedeltas
from dateutil import parser
## import local files
from ogd.common.utils.helpers import Capitalize
from ogd.common.utils.Logger import Logger

class To:
    @staticmethod
    @abc.abstractmethod
    def convert(name:str, value:Any, force:bool=False):
        pass

    @classmethod
    def supported(cls, to_type:type | str) -> bool:
        return "ANY"               in cls._supported() \
            or Capitalize(to_type) in cls._supported()

    @staticmethod
    @abc.abstractmethod
    def _supported() -> typing.Set[type | str]:
        pass

class Bool(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[bool]:
        """Attempt to turn a given value into a bool

        Returns None if the value type was not recognized

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a bool representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `bool` constructor on the `value`.
            Defaults to False.
        :type force: bool
        :return: The bool representation of value, if type of value was recognized, else None
        :rtype: Optional[bool]
        """
        ret_val : Optional[bool]

        match value:
            case bool():
                ret_val = value
            case int() | float():
                ret_val = bool(value)
            case str():
                ret_val = Bool.FromString(bool_str=value)
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a bool, float, int, or string!"
                if force:
                    ret_val = Bool.FromString(str(value))
                    msg = f"{base_msg} Defaulting to BoolFromString(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
        return ret_val

    @staticmethod
    def _supported() -> typing.Set[type | str]:
        return {bool, int, float, str, "BOOL", "INT", "FLOAT", "STR"}

    @staticmethod
    def FromString(bool_str:str) -> bool:
        ret_val : bool

        match bool_str.upper():
            case 'TRUE' | 'YES':
                ret_val = True
            case 'FALSE' | 'NO':
                ret_val = False
            case _:
                ret_val = bool(bool_str)
        return ret_val

class Int(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[int]:
        """Attempt to turn a given value into an int

        Returns None if the value type was not recognized

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to an int representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `int` constructor on the `value`, which may raise error.
            If the constructor errors, None will be returned anyway.
            Defaults to False.
        :type force: bool
        :return: The int representation of value, if type of value was recognized, else None
        :rtype: Optional[int]
        """
        ret_val : Optional[int]

        try:
            match value:
                case int():
                    ret_val = value
                case float():
                    ret_val = int(round(value))
                    Logger.Log(f"{name} was a float value, rounding to nearest int: {ret_val}.", logging.DEBUG)
                case str():
                    ret_val = int(value)
                case _:
                    base_msg : str = f"{name} was unexpected type {type(value)}, expected a float, int, or string!"
                    if force:
                        ret_val = int(value)
                        msg = f"{base_msg} Defaulting to int(value) == {ret_val}."
                    else:
                        ret_val = None
                        msg = f"{base_msg} Defaulting to None."
                    Logger.Log(msg, logging.WARN)
        except ValueError as err:
            Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to int, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
            ret_val = None
        return ret_val

    @staticmethod
    def _supported() -> typing.Set[type | str]:
        return {int, float, str, "INT", "FLOAT", "STR"}

class Float(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[float]:
        """Attempt to turn a given value into a float

        Returns None if the value type was not recognized

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a float representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `float` constructor on the `value`.
            If the constructor errors, None will be returned anyway.
            Defaults to False.
        :type force: bool
        :return: The float representation of value, if type of value was recognized, else None
        :rtype: Optional[float]
        """
        ret_val : Optional[float]

        try:
            match value:
                case float():
                    ret_val = value
                case int():
                    ret_val = float(value)
                case str():
                    ret_val = float(value)
                case _:
                    base_msg : str = f"{name} was unexpected type {type(value)}, expected a float, int, or string!"
                    if force:
                        ret_val = float(value)
                        msg = f"{base_msg} Defaulting to float(value) == {ret_val}."
                    else:
                        ret_val = None
                        msg = f"{base_msg} Defaulting to None."
                    Logger.Log(msg, logging.WARN)
        except ValueError as err:
            Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to float, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
            ret_val = None
        return ret_val

    @staticmethod
    def _supported() -> typing.Set[type | str]:
        return {int, float, str, "INT", "FLOAT", "STR"}

class String(To):
    @staticmethod
    def convert(name:str, value:Any) -> str:
        """Attempt to turn a given value into a str

        Returns None if the value type was not recognized.
        This is a cheat, relative to other `To<Type>` functions in the class,
        because anything that is not a string will be converted with str(value).

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a str representation
        :type value: Any
        :return: The str representation of value, if type of value was recognized, else None
        :rtype: Optional[str]
        """
        ret_val : str

        match value:
            case str():
                ret_val = value
            case _:
                ret_val = str(value)
                # Logger.Log(f"{name} was unexpected type {type(value)}, expected a string! Defaulting to str(value) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _supported() -> typing.Set[Type | str]:
        return {"ANY"}

class Path(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[pathlib.Path]:
        """Attempt to turn a given value into a path

        Returns None if the value type was not recognized.

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a path representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `Path` constructor on the `value`.
            If the constructor errors, None will be returned anyway.
            Defaults to False.
        :type force: bool
        :return: The path representation of value, if type of value was recognized, else None
        :rtype: Optional[path]
        """
        ret_val : Optional[pathlib.Path]

        try:
            match value:
                case pathlib.Path():
                    ret_val = value
                case str():
                    ret_val = pathlib.Path(value)
                case _:
                    base_msg : str = f"{name} was unexpected type {type(value)}, expected a Path or string!"
                    if force:
                        ret_val = pathlib.Path(str(value))
                        msg = f"{base_msg} Defaulting to Path(str(value)) == {ret_val}."
                    else:
                        ret_val = None
                        msg = f"{base_msg} Defaulting to None."
                    Logger.Log(msg, logging.WARN)
        except TypeError as err:
            Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to Path, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
            ret_val = None
        return ret_val

    @staticmethod
    def _supported() -> typing.Set[type | str]:
        return {pathlib.Path, str, "PATH", "STR"}

class List(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[typing.List]:
        """Attempt to turn a given value into a list

        Returns None if the value type was not recognized.

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a list representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `typing.List` constructor on the `value`.
            If the constructor errors, None will be returned anyway.
            Defaults to False.
        :type force: bool
        :return: The list representation of value, if type of value was recognized, else None
        :rtype: Optional[typing.List]
        """
        ret_val : Optional[typing.List]
        try:
            match value:
                case list():
                    # if input was a list already, then just give it back. Else, try to load it from string.
                    ret_val = value
                case set():
                    ret_val = list(value)
                case str():
                    if value not in {'None', 'null', ''}: # watch out for nasty corner cases.
                        ret_val = list(json.loads(value))
                    else:
                        ret_val = None
                case _:
                    base_msg : str = f"{name} was unexpected type {type(value)}, expected a list or string!"
                    if force:
                        ret_val = list(json.loads(str(value)))
                        msg = f"{base_msg} Defaulting to list(json.loads(str(value))) == {ret_val}."
                    else:
                        ret_val = None
                        msg = f"{base_msg} Defaulting to None."
                    Logger.Log(msg, logging.WARN)
        except JSONDecodeError as err:
            Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to list, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
            ret_val = None
        return ret_val

    @staticmethod
    def _supported() -> typing.Set[type | str]:
        return {list, set, str, "LIST", "SET", "STR"}

class JSON(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False, sort:bool=False) -> Optional[Dict]:
        """Attempt to turn a given value into a JSON-style dictionary

        Returns None if the value type was not recognized.

        .. TODO: Add a 'sanitize' param to purge anything that looks like an IP address or other pii

        :param name: An identifier for the value, used for debug outputs.
        :type name: str
        :param value: The value to parse to a JSON representation
        :type value: Any
        :param force: Flag for how to handle cases where the type of `value` is not directly handled by the function.  
            If False, return None when such cases arise. If True, attempt to use `Dict` constructor on the `value`.
            If the constructor errors, None will be returned anyway.
            Defaults to False.
        :type force: bool
        :return: The JSON representation of value, if type of value was recognized, else None
        :rtype: Optional[Dict]
        """
        ret_val : Optional[Dict]
        try:
            match value:
                case dict():
                    # if input was a dict already, then just give it back. Else, try to load it from string.
                    ret_val = value
                case str():
                    if value not in {'None', ''}: # watch out for nasty corner cases.
                        ret_val = json.loads(value)
                    else:
                        ret_val = None
                case _:
                    base_msg : str = f"{name} was unexpected type {type(value)}, expected a dict or string!"
                    if force:
                        ret_val = json.loads(str(value))
                        msg = f"{base_msg} Defaulting to json.loads(str(value)) == {ret_val}."
                    else:
                        ret_val = None
                        msg = f"{base_msg} Defaulting to None."
                    Logger.Log(msg, logging.WARN)
        except JSONDecodeError as err:
            Logger.Log(f"{name} with value '{value}' of type {type(value)} could not be converted to JSON, got the following error:\n{str(err)}\nDefaulting to None", logging.WARN)
            ret_val = None
        if sort and ret_val is not None:
            ret_val = dict(sorted(ret_val.items()))
        return ret_val

    @staticmethod
    def _supported() -> typing.Set[type | str]:
        return {dict, str, "DICT", "JSON", "STR"}

class Date(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[datetime.date]:
        ret_val : Optional[datetime.date]

        match value:
            case datetime.date():
                ret_val = value
            case _:
                converted = Datetime.convert(name=name, value=value, force=force)
                ret_val = converted.date() if converted is not None else None
        
        return ret_val

class Datetime(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[datetime.datetime]:
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

        match value:
            case datetime.datetime():
                ret_val = value
            case datetime.date():
                midnight = datetime.datetime.min.time()
                ret_val = datetime.datetime.combine(date=value, time=midnight)
                Logger.Log(f"{name} was a date value, defaulting to midnight of the given date: {ret_val}", logging.WARN)
            case str():
                ret_val = Datetime.DatetimeFromString(time_str=value)
            case timestamps.Timestamp():
                ret_val = value.to_pydatetime()
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a datetime or string!"
                if force:
                    ret_val = Datetime.DatetimeFromString(str(value))
                    msg = f"{base_msg} Defaulting to DatetimeFromString(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
        return ret_val

    @staticmethod
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

class Timedelta(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[datetime.timedelta]:
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
        match value:
            case datetime.timedelta():
                ret_val = value
            case datetime.time():
                ret_val = value - datetime.datetime.min.time()
                Logger.Log(f"{name} was a time value, treating the time is difference from 0: {ret_val}", logging.WARN)
            case str():
                ret_val = Timedelta.TimedeltaParser.FromString(time_str=value)
            case int():
                ret_val = datetime.timedelta(seconds=value)
            case timedeltas.Timedelta():
                ret_val = value.to_pytimedelta()
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a timedelta, time, or string!"
                if force:
                    ret_val = Timedelta.TimedeltaParser.FromString(str(value))
                    msg = f"{base_msg} Defaulting to TimedeltaFromString(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
        return ret_val

    class TimedeltaParser:
        _PATTERN = None

        @staticmethod
        def PATTERN() -> re.Pattern:
            if Timedelta.TimedeltaParser._PATTERN is None:
                neg_pattern    : LiteralString = r"(?P<neg>-)"
                day_pattern    : LiteralString = r"(?:(?P<day>\d+)\s+day(?:s)?,\s+)"
                hour_pattern   : LiteralString = r"(?P<hour>\d+)"
                minute_pattern : LiteralString = r"(?P<minute>\d+)"
                second_pattern : LiteralString = r"(?P<second>\d+)"
                micros_pattern : LiteralString = r"(?P<micros>\d+)"
                Timedelta.TimedeltaParser._PATTERN = re.compile(f"{neg_pattern}?{day_pattern}?{hour_pattern}:{minute_pattern}(:{second_pattern}(\\.{micros_pattern})?)?")
            return Timedelta.TimedeltaParser._PATTERN

        @staticmethod
        def FromString(time_str:str) -> Optional[datetime.timedelta]:
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
                    Timedelta.TimedeltaParser.FromRegex,
                    Timedelta.TimedeltaParser.FromSeconds,
                    Timedelta.TimedeltaParser.FromPandas,
                    Timedelta.TimedeltaParser.FromDateutil
                ]
                parser_iterator = (td for p in parsers if (td := p(time_str)) is not None)
                ret_val = next(parser_iterator, None)
                if ret_val is None:
                    Logger.Log(f"Could not parse timedelta '{time_str}' of type {type(time_str)}, it did not match any expected formats.", logging.WARNING)
            
            return ret_val

        @staticmethod
        def FromRegex(time_str:str) -> Optional[datetime.timedelta]:
            ret_val = None

            match = re.fullmatch(pattern=Timedelta.TimedeltaParser.PATTERN(), string=time_str)
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
                td = pandas.Timedelta(time_str)
            except ValueError:
                pass # if we got a bad string, then fine, we'll just return None
            else:
                ret_val = td.to_pytimedelta()

            return ret_val

class Timezone(To):
    @staticmethod
    def convert(name:str, value:Any, force:bool=False) -> Optional[datetime.timezone]:
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
        match value:
            case datetime.timezone():
                ret_val = value
            case datetime.timedelta():
                ret_val = datetime.timezone(value)
            case str():
                ret_val = Timezone.TimezoneParser.FromString(time_str=value)
            case _:
                base_msg : str = f"{name} was unexpected type {type(value)}, expected a float, int, or string!"
                if force:
                    ret_val = Timezone.TimezoneParser.FromString(str(value))
                    msg = f"{base_msg} Defaulting to TimezoneFromString(str(value)) == {ret_val}."
                else:
                    ret_val = None
                    msg = f"{base_msg} Defaulting to None."
                Logger.Log(msg, logging.WARN)
        return ret_val

    class TimezoneParser:

        _PATTERN = None

        @staticmethod
        def PATTERN() -> re.Pattern:
            if Timezone.TimezoneParser._PATTERN is None:
                utc_pattern    : LiteralString = r"(?P<utc>UTC)"
                dir_pattern    : LiteralString = r"(?P<dir>\+|-)"
                day_pattern    : LiteralString = r"(?:(?P<day>\d+)\s+day(?:s)?,\s+)"
                hour_pattern   : LiteralString = r"(?P<hour>\d+)"
                minute_pattern : LiteralString = r"(?P<minute>\d+)"
                second_pattern : LiteralString = r"(?P<second>\d+)"
                micros_pattern : LiteralString = r"(?P<micros>\d+)"
                raw_pattern = f"{utc_pattern}?{dir_pattern}?{day_pattern}?{hour_pattern}:{minute_pattern}:{second_pattern}(\\.{micros_pattern})?"

                Timezone.TimezoneParser._PATTERN = re.compile(raw_pattern)
            return Timezone.TimezoneParser._PATTERN

        @staticmethod
        def FromString(time_str:str) -> Optional[datetime.timezone]:
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
                    Timezone.TimezoneParser.FromRegex,
                    Timezone.TimezoneParser.FromSeconds,
                    Timezone.TimezoneParser.FromTimedeltaString
                ]
                parser_iterator = (td for p in parsers if (td := p(time_str)) is not None)
                ret_val = next(parser_iterator, None)
                if ret_val is None:
                    Logger.Log(f"Could not parse timezone '{time_str}' of type {type(time_str)}, it did not match any expected formats.", logging.WARNING)

                return ret_val
        
        @staticmethod
        def FromRegex(time_str:str) -> Optional[datetime.timezone]:
            ret_val = None

            match = re.fullmatch(pattern=Timezone.TimezoneParser.PATTERN(), string=time_str)
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
                ret_val = Timezone.TimezoneParser._offsetToTimezone(offset=offset)

            return ret_val

        @staticmethod
        def FromSeconds(time_str:str) -> Optional[datetime.timezone]:
            ret_val = None

            match = re.fullmatch(pattern=r"-?\d+", string=time_str)
            if match:
                offset = datetime.timedelta(seconds=int(time_str))
                ret_val = Timezone.TimezoneParser._offsetToTimezone(offset=offset)
            
            return ret_val
        
        @staticmethod
        def FromTimedeltaString(time_str:str) -> Optional[datetime.timezone]:
            ret_val = None

            time_str = time_str.removeprefix("UTC")
            time_str = time_str.removeprefix("+")
            offset = Timedelta.TimedeltaParser.FromString(time_str=time_str)
            if offset:
                ret_val = Timezone.TimezoneParser._offsetToTimezone(offset=offset)

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
