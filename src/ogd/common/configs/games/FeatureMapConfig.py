# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.common.configs.games.AggregateConfig import AggregateConfig
from ogd.common.configs.games.PerCountConfig import PerCountConfig
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class FeatureMapConfig(Schema):
    """
    Dumb struct to contain the specification and config of a set of features for a game.
    """

    _DEFAULT_LEGACY_MODE = False
    _DEFAULT_LEGACY_FEATS = {}
    _DEFAULT_PERCOUNT_FEATS = {}
    _DEFAULT_AGGREGATE_FEATS = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, legacy_mode: bool,        legacy_perlevel_feats:Dict[str, PerCountConfig],
                 percount_feats:Dict[str, PerCountConfig], aggregate_feats:Dict[str, AggregateConfig],
                 other_elements:Optional[Map]=None):
        self._legacy_mode           : bool                       = legacy_mode
        self._legacy_perlevel_feats : Dict[str, PerCountConfig]  = legacy_perlevel_feats
        self._percount_feats        : Dict[str, PerCountConfig]  = percount_feats
        self._aggregate_feats       : Dict[str, AggregateConfig] = aggregate_feats

        super().__init__(name=name, other_elements=other_elements)

    @property
    def LegacyMode(self) -> bool:
        return self._legacy_mode

    @property
    def LegacyPerLevelFeatures(self) -> Dict[str, PerCountConfig]:
        return self._legacy_perlevel_feats

    @property
    def PerCountFeatures(self) -> Dict[str, PerCountConfig]:
        return self._percount_feats

    @property
    def AggregateFeatures(self) -> Dict[str, AggregateConfig]:
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

    @classmethod
    def FromDict(cls, name:str, all_elements:Dict[str, Any], logger:Optional[logging.Logger]=None)-> "FeatureMapConfig":
        _legacy_mode           : bool
        _legacy_perlevel_feats : Dict[str, PerCountConfig]
        _percount_feats        : Dict[str, PerCountConfig]
        _aggregate_feats       : Dict[str, AggregateConfig]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For FeatureMap config of `{name}`, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        _legacy_mode = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["legacy"],
            to_type=cls._parseLegacyMode,
            default_value=cls._DEFAULT_LEGACY_MODE
        )
        _legacy_perlevel_feats = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["perlevel", "per_level"],
            to_type=cls._parsePerLevelFeatures,
            default_value=cls._DEFAULT_LEGACY_FEATS
        )
        _percount_feats = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["per_count", "percount"],
            to_type=cls._parsePerCountFeatures,
            default_value=cls._DEFAULT_PERCOUNT_FEATS
        )
        _aggregate_feats = cls.ParseElement(unparsed_elements=all_elements, logger=logger,
            valid_keys=["aggregate"],
            to_type=cls._parseAggregateFeatures,
            default_value=cls._DEFAULT_AGGREGATE_FEATS
        )

        _used = {"legacy", "perlevel", "per_count", "aggregate"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        return FeatureMapConfig(name=name, legacy_mode=_legacy_mode, legacy_perlevel_feats=_legacy_perlevel_feats,
                                percount_feats=_percount_feats, aggregate_feats=_aggregate_feats,
                                other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "FeatureMapConfig":
        return FeatureMapConfig(
            name="DefaultFeatureMapConfig",
            legacy_mode=cls._DEFAULT_LEGACY_MODE,
            legacy_perlevel_feats=cls._DEFAULT_LEGACY_FEATS,
            percount_feats=cls._DEFAULT_PERCOUNT_FEATS,
            aggregate_feats=cls._DEFAULT_AGGREGATE_FEATS,
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
    def _parseLegacyMode(legacy_element) -> bool:
        ret_val : bool
        if isinstance(legacy_element, dict):
            ret_val = legacy_element.get("enabled", False)
        else:
            ret_val = bool(legacy_element)
            Logger.Log(f"LegacyMode element was not a dict, defaulting to bool(legacy_element) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePerLevelFeatures(perlevels) -> Dict[str, PerCountConfig]:
        ret_val : Dict[str, PerCountConfig]
        if isinstance(perlevels, dict):
            ret_val = { key : PerCountConfig.FromDict(name=key, unparsed_elements=val) for key,val in perlevels.items() }
        else:
            ret_val = {}
            Logger.Log("Per-level features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePerCountFeatures(percounts) -> Dict[str, PerCountConfig]:
        ret_val : Dict[str, PerCountConfig]
        if isinstance(percounts, dict):
            ret_val = { key : PerCountConfig.FromDict(name=key, unparsed_elements=val) for key,val in percounts.items() }
        else:
            ret_val = {}
            Logger.Log("Per-count features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    @staticmethod
    def _parseAggregateFeatures(aggregates) -> Dict[str, AggregateConfig]:
        ret_val : Dict[str, AggregateConfig]
        if isinstance(aggregates, dict):
            ret_val = {key : AggregateConfig(name=key, other_elements=val) for key,val in aggregates.items()}
        else:
            ret_val = {}
            Logger.Log("Per-count features map was not a dict, defaulting to empty dict", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
