# import standard libraries
import logging
from typing import Any, Dict, List, Optional
# import local files
from ogd.common.schemas.games.DetectorSchema import DetectorSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class DetectorMapSchema(Schema):

    # *** BUILT-INS & PROPERTIES ***

    """
    Dumb struct to contain the specification and config of a set of features for a game.
    """
    def __init__(self, name:str,
                 perlevel_detectors:Dict[str, DetectorSchema], percount_detectors:Dict[str, DetectorSchema], aggregate_detectors:Dict[str, DetectorSchema],
                 other_elements:Dict[str, Any]):
        self._perlevel_detectors  : Dict[str, DetectorSchema] = perlevel_detectors
        self._percount_detectors  : Dict[str, DetectorSchema] = percount_detectors
        self._aggregate_detectors : Dict[str, DetectorSchema] = aggregate_detectors

        super().__init__(name=name, other_elements=other_elements)

    @property
    def PerLevelDetectors(self) -> Dict[str, DetectorSchema]:
        return self._perlevel_detectors

    @property
    def PerCountDetectors(self) -> Dict[str, DetectorSchema]:
        return self._percount_detectors

    @property
    def AggregateDetectors(self) -> Dict[str, DetectorSchema]:
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
    def AsDict(self) -> Dict[str, Dict[str, DetectorSchema]]:
        ret_val = {
            "perlevel"  : self.PerLevelDetectors,
            "per_count" : self.PerCountDetectors,
            "aggregate" : self.AggregateDetectors
        }
        return ret_val

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "DetectorMapSchema":
        _perlevel_detectors  : Dict[str, DetectorSchema]
        _percount_detectors  : Dict[str, DetectorSchema]
        _aggregate_detectors : Dict[str, DetectorSchema]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For DetectorMap config of `{name}`, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "perlevel" in all_elements.keys():
            _perlevel_detectors = DetectorMapSchema._parsePerLevelDetectors(perlevels=all_elements['perlevel'])
        else:
            Logger.Log(f"DetectorMap config does not have a 'perlevel' element; defaulting to empty dictionary", logging.WARN)
            _perlevel_detectors = {}
        if "per_count" in all_elements.keys():
            _percount_detectors = DetectorMapSchema._parsePerCountDetectors(percounts=all_elements['per_count'])
        else:
            Logger.Log(f"DetectorMap config does not have a 'per_count' element; defaulting to empty dictionary", logging.WARN)
            _percount_detectors = {}
        if "aggregate" in all_elements.keys():
            _aggregate_detectors = DetectorMapSchema._parseAggregateDetectors(aggregates=all_elements['aggregate'])
        else:
            Logger.Log(f"DetectorMap config does not have an 'aggregate' element; defaulting to empty dictionary", logging.WARN)
            _aggregate_detectors = {}
        _used = {"legacy", "perlevel", "per_count", "aggregate"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return DetectorMapSchema(name=name, perlevel_detectors=_perlevel_detectors,
                                 percount_detectors=_percount_detectors, aggregate_detectors=_aggregate_detectors,
                                 other_elements=_leftovers)

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
    def _parsePerLevelDetectors(perlevels) -> Dict[str, DetectorSchema]:
        ret_val : Dict[str, DetectorSchema]
        if isinstance(perlevels, dict):
            ret_val = { key : DetectorSchema(name=key, all_elements=val) for key,val in perlevels.items() }
        else:
            ret_val = {}
            Logger.Log(f"Per-level detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parsePerCountDetectors(percounts) -> Dict[str, DetectorSchema]:
        ret_val : Dict[str, DetectorSchema]
        if isinstance(percounts, dict):
            ret_val = { key : DetectorSchema(name=key, all_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log(f"Per-count detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseAggregateDetectors(aggregates) -> Dict[str, DetectorSchema]:
        ret_val : Dict[str, DetectorSchema]
        if isinstance(aggregates, dict):
            ret_val = {key : DetectorSchema(name=key, all_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log(f"Per-count detectors map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
