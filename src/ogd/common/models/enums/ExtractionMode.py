# import standard libraries
from enum import IntEnum

class ExtractionMode(IntEnum):
    """Simple enum to represent the different levels of granularity at which extractions can be carried out:
    Session, Player, Population.

    At some point in the future, goal will be to replace `AggregationMode` with `Aggregator`,
    which will just define some sort of rule for dividing events up into smaller bunches.
    These will probably just exist at the `ogd-core` level, and `AggregationMode` will be deprecated and removed from `ogd-common`.
    """
    SESSION = 1
    PLAYER = 2
    POPULATION = 3

    def __str__(self):
        return self.name
