# import standard libraries
import logging
from typing import Dict, Optional
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.generators.DetectorConfig import DetectorConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class DetectorMapConfig(Config):
    _DEFAULT_PERCOUNT_DETECTORS  = {}
    _DEFAULT_AGGREGATE_DETECTORS = {}

    # *** BUILT-INS & PROPERTIES ***

    """
    Dumb struct to contain the specification and config of a set of features for a game.
    """
    def __init__(self, name:str,
                 percount_detectors:Dict[str, DetectorConfig], aggregate_detectors:Dict[str, DetectorConfig],
                 other_elements:Optional[Map]=None):
        self._percount_detectors  : Dict[str, DetectorConfig] = percount_detectors or self._parsePerCountDetectors(unparsed_elements=other_elements or {})
        self._aggregate_detectors : Dict[str, DetectorConfig] = aggregate_detectors or self._parseAggregateDetectors(unparsed_elements=other_elements or {})

        super().__init__(name=name, other_elements=other_elements)

    @property
    def PerCountDetectors(self) -> Dict[str, DetectorConfig]:
        return self._percount_detectors

    @property
    def AggregateDetectors(self) -> Dict[str, DetectorConfig]:
        return self._aggregate_detectors

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        feature_summary = ["## Processed Features",
                           "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        feature_list = [feature.AsMarkdown for feature in self._aggregate_detectors.values()] + [feature.AsMarkdown for feature in self._percount_detectors.values()]
        feature_list = feature_list if len(feature_list) > 0 else ["None"]
        return "  \n\n".join(feature_summary + feature_list)

    @property
    def AsDict(self) -> Dict[str, Dict[str, DetectorConfig]]:
        ret_val = {
            "per_count" : self.PerCountDetectors,
            "aggregate" : self.AggregateDetectors
        }
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "DetectorMapConfig":
        """Function to generate a DetectorMapConfig from a JSON-formatted dictionary.

        Expected structure is:
        {
            "per_count" : {
                "example" : {
                    "type":"ExampleDetectorClass",
                    "enabled":true,
                    "description":"Info about the per-count detector; the per-count is generally optional."
                }
            },
            "aggregate" : {
                "example" : {
                    "type":"ExampleDetectorClass",
                    "enabled":true,
                    "description":"Info about the aggregate (session-level) detector."
                }
            },
        }

        :param name: The name of the detector map configuration.
        :type name: str
        :param unparsed_elements: Elements of the source dictionary that have not yet been parsed, and will be used to construct the config.
        :type unparsed_elements: Map
        :return: A DetectorMapConfig based on the given collection of elements.
        :rtype: DetectorMapConfig
        """
        _percount_detectors  : Dict[str, DetectorConfig] = cls._parsePerCountDetectors(unparsed_elements=unparsed_elements)
        _aggregate_detectors : Dict[str, DetectorConfig] = cls._parseAggregateDetectors(unparsed_elements=unparsed_elements)

        _used = {"per_count", "percount", "aggregate"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return DetectorMapConfig(name=name,
                                 percount_detectors=_percount_detectors, aggregate_detectors=_aggregate_detectors,
                                 other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "DetectorMapConfig":
        return DetectorMapConfig(
            name="DefaultDetectorMapConfig",
            percount_detectors=cls._DEFAULT_PERCOUNT_DETECTORS,
            aggregate_detectors=cls._DEFAULT_AGGREGATE_DETECTORS,
            other_elements={}
        )

    # TODO : Bring back AsMarkdownRow for markdown table approach to representing game schemas.
    # @property
    # def AsMarkdownRow(self) -> str:
    #     ret_val : str = f"| {self.Name} | {self.ElementType} | {self.Description} |"
    #     if self.Details is not None:
    #         detail_markdowns = [f"**{name}** : {desc}" for name,desc in self.Details.items()]
    #         ret_val += ', '.join(detail_markdowns)
    #     ret_val += " |"
    #     return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parsePerCountDetectors(unparsed_elements:Map) -> Dict[str, DetectorConfig]:
        ret_val : Dict[str, DetectorConfig]

        percounts = DetectorMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["per_count", "percount"],
            to_type=dict,
            default_value=DetectorMapConfig._DEFAULT_PERCOUNT_DETECTORS
        )
        if isinstance(percounts, dict):
            ret_val = { key : DetectorConfig.FromDict(name=key, unparsed_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log("Per-count detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parseAggregateDetectors(unparsed_elements:Map) -> Dict[str, DetectorConfig]:
        ret_val : Dict[str, DetectorConfig]

        aggregates = DetectorMapConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["aggregate"],
            to_type=dict,
            default_value=DetectorMapConfig._DEFAULT_AGGREGATE_DETECTORS
        )
        if isinstance(aggregates, dict):
            ret_val = {key : DetectorConfig.FromDict(name=key, unparsed_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log("Aggregate detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
