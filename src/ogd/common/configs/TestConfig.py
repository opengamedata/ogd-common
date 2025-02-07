"""
TestConfig

Contains a Schema class for managing config data for testing configurations.
In particular, base testing config files always have a `"VERBOSE"` setting,
and a listing of `"ENABLED"` tests.
"""

# import standard libraries
import logging
from typing import Any, Dict, Optional

# import 3rd-party libraries

# import OGD libraries
from ogd.common.configs.Config import Config
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

# import local files

class TestConfig(Config):
    _DEFAULT_VERBOSE       = False
    _DEFAULT_ENABLED_TESTS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, verbose:bool, enabled_tests:Dict[str, bool], other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}

        self._verbose       : bool            = verbose
        self._enabled_tests : Dict[str, bool] = enabled_tests
        super().__init__(name=name, other_elements=unparsed_elements)

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
    def Default(cls) -> "TestConfig":
        return TestConfig(
            name            = "DefaultTestConfig",
            verbose         = cls._DEFAULT_VERBOSE,
            enabled_tests   = cls._DEFAULT_ENABLED_TESTS
        )

    # *** PUBLIC STATICS ***

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "TestConfig":
        _verbose         : bool
        _enabled_tests   : Dict[str, bool]

        if not isinstance(all_elements, dict):
            all_elements = {}
            _msg = f"For {name} testing config, all_elements was not a dict, defaulting to empty dict"
            if logger:
                logger.warning(_msg)
            else:
                Logger.Log(_msg, logging.WARN)
        _verbose = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["VERBOSE"],
            to_type=cls._parseVerbose,
            default_value=cls._DEFAULT_VERBOSE
        )
        _enabled_tests = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["ENABLED"],
            to_type=cls._parseEnabledTests,
            default_value=cls._DEFAULT_ENABLED_TESTS
        )

        _used = {"VERBOSE", "ENABLED"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return TestConfig(name=name, verbose=_verbose, enabled_tests=_enabled_tests, other_elements=_leftovers)

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseVerbose(unparsed_elements:Map) -> bool:
        return TestConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["VERBOSE"],
            to_type=bool,
            default_value=TestConfig._DEFAULT_VERBOSE,
            remove_target=True
        )

    @staticmethod
    def _parseEnabledTests(unparsed_elements:Map) -> Dict[str, bool]:
        ret_val : Dict[str, bool]

        enabled = TestConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["ENABLED"],
            to_type=dict,
            default_value=TestConfig._DEFAULT_ENABLED_TESTS,
            remove_target=True
        )
        ret_val = { str(key) : conversions.ConvertToType(value=val, to_type=bool, name=key) for key, val in enabled.items() }

        return ret_val

    # *** PRIVATE METHODS ***
