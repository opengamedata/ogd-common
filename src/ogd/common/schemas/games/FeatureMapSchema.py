# import standard libraries
import logging
from typing import Any, Dict, List, Optional
# import local files
from ogd.common.schemas.games.AggregateSchema import AggregateSchema
from ogd.common.schemas.games.PerCountSchema import PerCountSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger

class FeatureMapSchema(Schema):
    """
    Dumb struct to contain the specification and config of a set of features for a game.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, legacy_mode: bool,        legacy_perlevel_feats:Dict[str, PerCountSchema],
                 percount_feats:Dict[str, PerCountSchema], aggregate_feats:Dict[str, AggregateSchema],
                 other_elements:Dict[str, Any]):
        self._legacy_mode           : bool                       = legacy_mode
        self._legacy_perlevel_feats : Dict[str, PerCountSchema]  = legacy_perlevel_feats
        self._percount_feats        : Dict[str, PerCountSchema]  = percount_feats
        self._aggregate_feats       : Dict[str, AggregateSchema] = aggregate_feats

        super().__init__(name=name, other_elements=other_elements)

    @property
    def LegacyMode(self) -> bool:
        return self._legacy_mode

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str, PerCountSchema]:
        return self._legacy_perlevel_feats

    @property
    def PerCountFeatures(self) -> Dict[str, PerCountSchema]:
        return self._percount_feats

    @property
    def AggregateFeatures(self) -> Dict[str, AggregateSchema]:
        return self._aggregate_feats

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        feature_summary = ["## Processed Features",
                           "The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run."
                          ]
        feature_list = [feature.AsMarkdown for feature in self._aggregate_feats.values()] + [feature.AsMarkdown for feature in self._percount_feats.values()]
        feature_list = feature_list if len(feature_list) > 0 else ["None"]
        return "  \n\n".join(feature_summary + feature_list)

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "FeatureMapSchema":
        _legacy_mode           : bool
        _legacy_perlevel_feats : Dict[str, PerCountSchema]
        _percount_feats        : Dict[str, PerCountSchema]
        _aggregate_feats       : Dict[str, AggregateSchema]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For FeatureMap config of `{name}`, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "legacy" in all_elements.keys():
            _legacy_mode = FeatureMapSchema._parseLegacyMode(legacy_element=all_elements['legacy'])
        else:
            Logger.Log(f"FeatureMap config does not have a 'legacy' element; defaulting to legacy=False", logging.WARN)
            _legacy_mode = False
        if "perlevel" in all_elements.keys():
            _legacy_perlevel_feats = FeatureMapSchema._parsePerLevelFeatures(perlevels=all_elements['perlevel'])
        else:
            Logger.Log(f"FeatureMap config does not have a 'perlevel' element; defaulting to empty dictionary", logging.WARN)
            _legacy_perlevel_feats = {}
        if "per_count" in all_elements.keys():
            _percount_feats = FeatureMapSchema._parsePerCountFeatures(percounts=all_elements['per_count'])
        else:
            Logger.Log(f"FeatureMap config does not have a 'per_count' element; defaulting to empty dictionary", logging.WARN)
            _percount_feats = {}
        if "aggregate" in all_elements.keys():
            _aggregate_feats = FeatureMapSchema._parseAggregateFeatures(aggregates=all_elements['aggregate'])
        else:
            Logger.Log(f"FeatureMap config does not have an 'aggregate' element; defaulting to empty dictionary", logging.WARN)
            _aggregate_feats = {}

        _used = {"legacy", "perlevel", "per_count", "aggregate"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return FeatureMapSchema(name=name, legacy_mode=_legacy_mode, legacy_perlevel_feats=_legacy_perlevel_feats,
                                percount_feats=_percount_feats, aggregate_feats=_aggregate_feats,
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
    def _parseLegacyMode(legacy_element) -> bool:
        ret_val : bool
        if isinstance(legacy_element, dict):
            ret_val = legacy_element.get("enabled", False)
        else:
            ret_val = bool(legacy_element)
            Logger.Log(f"LegacyMode element was not a dict, defaulting to bool(legacy_element) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parsePerLevelFeatures(perlevels) -> Dict[str, PerCountSchema]:
        ret_val : Dict[str, PerCountSchema]
        if isinstance(perlevels, dict):
            ret_val = { key : PerCountSchema(name=key, all_elements=val) for key,val in perlevels.items() }
        else:
            ret_val = {}
            Logger.Log(f"Per-level features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parsePerCountFeatures(percounts) -> Dict[str, PerCountSchema]:
        ret_val : Dict[str, PerCountSchema]
        if isinstance(percounts, dict):
            ret_val = { key : PerCountSchema(name=key, all_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log(f"Per-count features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseAggregateFeatures(aggregates) -> Dict[str, AggregateSchema]:
        ret_val : Dict[str, AggregateSchema]
        if isinstance(aggregates, dict):
            ret_val = {key : AggregateSchema(name=key, all_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log(f"Per-count features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
