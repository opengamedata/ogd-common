"""
TestConfig

Contains a Schema class for managing config data for testing configurations.
In particular, base testing config files always have a `"VERBOSE"` setting,
and a listing of `"ENABLED"` tests.
"""

# import standard libraries
from typing import Dict, Final, Optional, Self

# import 3rd-party libraries

# import OGD libraries
from ogd.common.configs.Config import Config
from ogd.common.utils.typing import Map, conversions

# import local files

class TestConfig(Config):
    _DEFAULT_VERBOSE       : Final[bool]            = False

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, verbose:Optional[bool], other_elements:Optional[Map]=None):
        """Constructor for the `TestConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "VERBOSE" : False,
            "ENABLED" : {
                "TEST1":True,
                "TEST2":True,
                ...
            }
        },
        ```

        :param name: _description_
        :type name: str
        :param verbose: _description_
        :type verbose: Optional[bool]
        :param enabled_tests: _description_
        :type enabled_tests: Optional[Dict[str, bool]]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._verbose       : bool            = verbose       if verbose       is not None else self._parseVerbose(unparsed_elements=unparsed_elements, schema_name=name)
        super().__init__(name=name, other_elements=unparsed_elements)

    @property
    def Verbose(self) -> bool:
        return self._verbose

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
            verbose         = cls._DEFAULT_VERBOSE
        )

    # *** PUBLIC STATICS ***

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "TestConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: TestConfig
        """
        return TestConfig(name=name, verbose=None, other_elements=unparsed_elements)

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseVerbose(unparsed_elements:Map, schema_name:Optional[str]=None) -> bool:
        return TestConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["VERBOSE"],
            to_type=bool,
            default_value=TestConfig._DEFAULT_VERBOSE,
            remove_target=True,
            schema_name=schema_name
        )

    # *** PRIVATE METHODS ***
