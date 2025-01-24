# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.games.DetectorConfig import DetectorConfig
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class DetectorMapConfig(Schema):
    _DEFAULT_PERLEVEL_DETECTORS  = {}
    _DEFAULT_PERCOUNT_DETECTORS  = {}
    _DEFAULT_AGGREGATE_DETECTORS = {}

    # *** BUILT-INS & PROPERTIES ***

    """
    Dumb struct to contain the specification and config of a set of features for a game.
    """
    def __init__(self, name:str,
                 perlevel_detectors:Dict[str, DetectorConfig], percount_detectors:Dict[str, DetectorConfig], aggregate_detectors:Dict[str, DetectorConfig],
                 other_elements:Optional[Map]=None):
        self._perlevel_detectors  : Dict[str, DetectorConfig] = perlevel_detectors
        self._percount_detectors  : Dict[str, DetectorConfig] = percount_detectors
        self._aggregate_detectors : Dict[str, DetectorConfig] = aggregate_detectors

        super().__init__(name=name, other_elements=other_elements)

    @property
    def PerLevelDetectors(self) -> Dict[str, DetectorConfig]:
        return self._perlevel_detectors

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
            "perlevel"  : self.PerLevelDetectors,
            "per_count" : self.PerCountDetectors,
            "aggregate" : self.AggregateDetectors
        }
        return ret_val

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "DetectorMapConfig":
        _perlevel_detectors  : Dict[str, DetectorConfig]
        _percount_detectors  : Dict[str, DetectorConfig]
        _aggregate_detectors : Dict[str, DetectorConfig]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For DetectorMap config of `{name}`, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        _perlevel_detectors = cls.ParseElement(all_elements=all_elements, logger=logger,
            valid_keys=["perlevel", "per_level"],
            value_type=cls._parsePerLevelDetectors,
            default_value=cls._DEFAULT_PERLEVEL_DETECTORS
        )
        _percount_detectors = cls.ParseElement(all_elements=all_elements, logger=logger,
            valid_keys=["per_count", "percount"],
            value_type=cls._parsePerCountDetectors,
            default_value=cls._DEFAULT_PERCOUNT_DETECTORS
        )
        _aggregate_detectors = cls.ParseElement(all_elements=all_elements, logger=logger,
            valid_keys=["aggregate"],
            value_type=cls._parseAggregateDetectors,
            default_value=cls._DEFAULT_AGGREGATE_DETECTORS
        )

        _used = {"perlevel", "per_level", "per_count", "percount", "aggregate"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return DetectorMapConfig(name=name, perlevel_detectors=_perlevel_detectors,
                                 percount_detectors=_percount_detectors, aggregate_detectors=_aggregate_detectors,
                                 other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "DetectorMapConfig":
        return DetectorMapConfig(
            name="DefaultDetectorMapConfig",
            perlevel_detectors=cls._DEFAULT_PERLEVEL_DETECTORS,
            percount_detectors=cls._DEFAULT_PERCOUNT_DETECTORS,
            aggregate_detectors=cls._DEFAULT_AGGREGATE_DETECTORS,
            other_elements={}
        )

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
    def _parsePerLevelDetectors(perlevels) -> Dict[str, DetectorConfig]:
        ret_val : Dict[str, DetectorConfig]
        if isinstance(perlevels, dict):
            ret_val = { key : DetectorConfig(name=key, all_elements=val) for key,val in perlevels.items() }
        else:
            ret_val = {}
            Logger.Log("Per-level detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePerCountDetectors(percounts) -> Dict[str, DetectorConfig]:
        ret_val : Dict[str, DetectorConfig]
        if isinstance(percounts, dict):
            ret_val = { key : DetectorConfig(name=key, all_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log("Per-count detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parseAggregateDetectors(aggregates) -> Dict[str, DetectorConfig]:
        ret_val : Dict[str, DetectorConfig]
        if isinstance(aggregates, dict):
            ret_val = {key : DetectorConfig(name=key, all_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log("Per-count detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
