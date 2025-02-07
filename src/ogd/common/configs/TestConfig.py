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

        self._verbose       : bool            = verbose       or self._parseVerbose(unparsed_elements=unparsed_elements)
        self._enabled_tests : Dict[str, bool] = enabled_tests or self._parseEnabledTests(unparsed_elements=unparsed_elements)
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
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "TestConfig":
        _verbose         : bool
        _enabled_tests   : Dict[str, bool]

        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            _msg = f"For {name} testing config, all_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)
        _verbose = cls._parseVerbose(unparsed_elements=unparsed_elements)
        _enabled_tests = cls._parseEnabledTests(unparsed_elements=unparsed_elements)

        return TestConfig(name=name, verbose=_verbose, enabled_tests=_enabled_tests, other_elements=unparsed_elements)

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
