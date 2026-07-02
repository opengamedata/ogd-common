## import standard libraries
import abc
import builtins
import datetime
import json
import logging
import pathlib
import typing
import re
import typing
from typing import Any, Dict, Literal, Optional, Type

from json.decoder import JSONDecodeError
## import 3rd-party libraries
from pandas import Timedelta
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
