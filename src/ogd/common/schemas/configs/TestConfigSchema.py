"""
TestConfigSchema

Contains a Schema class for managing config data for testing configurations.
In particular, base testing config files always have a `"VERBOSE"` setting,
and a listing of `"ENABLED"` tests.
"""

# import standard libraries
import logging
from typing import Any, Dict, Optional

# import 3rd-party libraries

# import OGD libraries
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

# import local files

class TestConfigSchema(Schema):
    _DEFAULT_VERBOSE       = False
    _DEFAULT_ENABLED_TESTS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, verbose:bool, enabled_tests:Dict[str, bool], other_elements:Dict[str, Any]={}):
        self._verbose       : bool            = verbose
        self._enabled_tests : Dict[str, bool] = enabled_tests
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Verbose(self) -> bool:
        return self._verbose

    @property
    def EnabledTests(self) -> Dict[str, bool]:
        return self._enabled_tests

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}"
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    
    @classmethod
    def Default(cls) -> "TestConfigSchema":
        return TestConfigSchema(
            name            = "DefaultTestConfig",
            verbose         = cls._DEFAULT_VERBOSE,
            enabled_tests   = cls._DEFAULT_ENABLED_TESTS
        )

    # *** PUBLIC STATICS ***

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "TestConfigSchema":
        _verbose         : bool
        _enabled_tests   : Dict[str, bool]

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} testing config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _verbose = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["VERBOSE"],
            parser_function=cls._parseVerbose,
            default_value=cls._DEFAULT_VERBOSE
        )
        _enabled_tests = cls.ElementFromDict(all_elements=all_elements, logger=logger,
            element_names=["ENABLED"],
            parser_function=cls._parseEnabledTests,
            default_value=cls._DEFAULT_ENABLED_TESTS
        )

        _used = {"VERBOSE", "ENABLED"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return TestConfigSchema(name=name, verbose=_verbose, enabled_tests=_enabled_tests, other_elements=_leftovers)

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseVerbose(verbose, logger:Optional[logging.Logger]=None) -> bool:
        ret_val : bool
        if isinstance(verbose, bool):
            ret_val = verbose
        elif isinstance(verbose, int):
            ret_val = bool(verbose)
        elif isinstance(verbose, str):
            ret_val = False if verbose.upper()=="FALSE" else bool(verbose)
        else:
            ret_val = bool(verbose)
            _msg = f"Config 'verbose' setting was unexpected type {type(verbose)}, defaulting to bool(verbose)={ret_val}."
            if logger:
                logger.warning(_msg, logging.WARN)
            else:
                print(_msg)
        return ret_val

    @staticmethod
    def _parseEnabledTests(enabled, logger:Optional[logging.Logger]=None) -> Dict[str, bool]:
        ret_val : Dict[str, bool]
        if isinstance(enabled, dict):
            ret_val = { str(key) : bool(val) for key, val in enabled.items() }
        else:
            ret_val = TestConfigSchema.Default().EnabledTests
            _msg = f"Config 'enabled tests' setting was unexpected type {type(enabled)}, defaulting to class default = {ret_val}."
            if logger:
                logger.warn(_msg, logging.WARN)
            else:
                print(_msg)
        return ret_val

    # *** PRIVATE METHODS ***
