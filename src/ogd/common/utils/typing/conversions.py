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
                ret_val  = to.Date.convert(name=name, value=value, force=force_conversion)
            case 'DATETIME' | datetime.datetime:
                ret_val = to.Datetime.convert(name=name, value=value, force=force_conversion)
            case 'TIMEDELTA' | datetime.timedelta:
                ret_val = to.Timedelta.convert(name=name, value=value, force=force_conversion)
            case 'TIMEZONE' | datetime.timezone:
                ret_val = to.Timezone.convert(name=name, value=value, force=force_conversion)
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
